/**
 * Hotelghino - Leaflet & OpenStreetMap Location Picker
 * Integración con CARTO Voyager (OpenStreetMap Data) y Nominatim.
 * Soluciona errores HTTP 403 (Access blocked) y asegura renderizado interactivo estable.
 */
(function() {
    'use strict';

    // Configurar rutas de iconos estándar de Leaflet desde CDN
    function setupLeafletIcons() {
        if (typeof L === 'undefined') return;
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
            iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
            iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
        });
    }

    function initHotelMapPicker() {
        const mapElement = document.getElementById('hotel-map');
        if (!mapElement) return;

        if (typeof L === 'undefined') {
            setTimeout(initHotelMapPicker, 80);
            return;
        }

        setupLeafletIcons();

        // Evitar doble inicialización si el mapa ya fue creado
        if (mapElement._leaflet_id) {
            return;
        }

        const inputSearch = document.getElementById('map-autocomplete-input');
        const searchResultsList = document.getElementById('map-search-results');
        const inputDirCompleta = document.getElementById('id_direccion_completa');
        const inputCiudad = document.getElementById('id_ciudad');
        const inputProvincia = document.getElementById('id_provincia');
        const inputCalle = document.getElementById('id_calle');
        const inputNumero = document.getElementById('id_numero_calle');
        const inputPais = document.getElementById('id_pais');
        const inputLat = document.getElementById('id_latitud');
        const inputLng = document.getElementById('id_longitud');
        const inputUbicacion = document.getElementById('id_ubicacion');
        const coordsText = document.getElementById('coords-text');
        const coordsBadge = document.getElementById('coords-status-badge');

        let initialLat = inputLat ? parseFloat(inputLat.value) : NaN;
        let initialLng = inputLng ? parseFloat(inputLng.value) : NaN;
        const hasInitialCoords = !isNaN(initialLat) && !isNaN(initialLng) && (initialLat !== 0 || initialLng !== 0);

        // Coordenadas iniciales: si tiene guardadas usa esas, sino centro en Argentina
        const defaultCenter = hasInitialCoords ? [initialLat, initialLng] : [-34.603722, -58.381592];
        const defaultZoom = hasInitialCoords ? 16 : 12;

        const map = L.map(mapElement, {
            center: defaultCenter,
            zoom: defaultZoom,
            zoomControl: true,
            scrollWheelZoom: true,
        });

        // Capa de mosaicos: CARTO Voyager oficial con soporte para CARTO_API_KEY
        const primaryTileLayer = (typeof window.createCartoTileLayer === 'function')
            ? window.createCartoTileLayer()
            : L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                subdomains: 'abcd',
                maxZoom: 20,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> colaboradores &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>'
            });

        primaryTileLayer.addTo(map);

        // Forzar recálculo de dimensiones del contenedor Leaflet
        setTimeout(function() { map.invalidateSize(); }, 150);
        setTimeout(function() { map.invalidateSize(); }, 400);
        setTimeout(function() { map.invalidateSize(); }, 800);
        window.addEventListener('resize', function() { map.invalidateSize(); });

        let marker = null;
        let lastReverseRequestTime = 0;

        function updateCoordinatesDisplay(lat, lng) {
            const formattedLat = Number(lat).toFixed(6);
            const formattedLng = Number(lng).toFixed(6);

            if (inputLat) inputLat.value = formattedLat;
            if (inputLng) inputLng.value = formattedLng;

            if (coordsText) {
                coordsText.textContent = `Coordenadas fijadas: ${formattedLat}, ${formattedLng}`;
            }
            if (coordsBadge) {
                coordsBadge.style.background = '#dcfce7';
                coordsBadge.style.color = '#15803d';
            }
        }

        function setMarkerPosition(lat, lng, shouldReverseGeocode) {
            lat = parseFloat(lat);
            lng = parseFloat(lng);
            if (isNaN(lat) || isNaN(lng)) return;

            if (!marker) {
                marker = L.marker([lat, lng], {
                    draggable: true,
                    title: 'Ubicación del hotel'
                }).addTo(map);

                marker.on('dragend', function() {
                    const pos = marker.getLatLng();
                    updateCoordinatesDisplay(pos.lat, pos.lng);
                    reverseGeocode(pos.lat, pos.lng);
                });
            } else {
                marker.setLatLng([lat, lng]);
            }

            updateCoordinatesDisplay(lat, lng);

            if (shouldReverseGeocode) {
                reverseGeocode(lat, lng);
            }
        }

        // Si ya tenía coordenadas guardadas (modo edición o recarga de form), colocar marcador
        if (hasInitialCoords) {
            setMarkerPosition(initialLat, initialLng, false);
        }

        // Selección haciendo clic en el mapa
        map.on('click', function(e) {
            setMarkerPosition(e.latlng.lat, e.latlng.lng, true);
        });

        // Geocodificación inversa con Nominatim (OpenStreetMap)
        function reverseGeocode(lat, lng) {
            const now = Date.now();
            // Respetar política de uso de Nominatim (1 req / seg)
            const delay = Math.max(0, 1000 - (now - lastReverseRequestTime));
            lastReverseRequestTime = now + delay;

            setTimeout(function() {
                const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lng)}&addressdetails=1&accept-language=es`;

                fetch(url, {
                    headers: { 'Accept': 'application/json' }
                })
                .then(function(res) {
                    if (!res.ok) throw new Error('Error en consulta de geocodificación inversa');
                    return res.json();
                })
                .then(function(data) {
                    if (!data || !data.address) return;
                    fillFieldsFromNominatim(data, false);
                })
                .catch(function(err) {
                    console.warn('Nominatim reverse error:', err);
                });
            }, delay);
        }

        function fillFieldsFromNominatim(item, centerMap) {
            const addr = item.address || {};
            const lat = parseFloat(item.lat);
            const lon = parseFloat(item.lon);

            if (centerMap && !isNaN(lat) && !isNaN(lon)) {
                map.setView([lat, lon], 16);
                setMarkerPosition(lat, lon, false);
            }

            // Dirección completa
            if (inputDirCompleta && item.display_name) {
                inputDirCompleta.value = item.display_name;
            }

            // Calle
            const calle = addr.road || addr.pedestrian || addr.street || addr.footway || addr.cycleway || '';
            if (inputCalle && calle) {
                inputCalle.value = calle;
            }

            // Número
            const numero = addr.house_number || '';
            if (inputNumero && numero) {
                inputNumero.value = numero;
            }

            // Ciudad / Localidad
            const ciudad = addr.city || addr.town || addr.village || addr.municipality || addr.suburb || addr.city_district || '';
            if (inputCiudad && ciudad) {
                inputCiudad.value = ciudad;
                if (inputUbicacion) {
                    inputUbicacion.value = ciudad;
                }
            }

            // Provincia / Región
            const provincia = addr.state || addr.province || addr.region || '';
            if (inputProvincia && provincia) {
                inputProvincia.value = provincia;
            }

            // País
            const pais = addr.country || 'Argentina';
            if (inputPais) {
                inputPais.value = pais;
            }
        }

        // Búsqueda de direcciones en tiempo real con Nominatim y debounce
        if (inputSearch && searchResultsList) {
            let debounceTimer = null;

            function hideResults() {
                searchResultsList.style.display = 'none';
                searchResultsList.innerHTML = '';
            }

            function searchNominatim(query) {
                if (!query || query.trim().length < 3) {
                    hideResults();
                    return;
                }

                const loadingLi = document.createElement('li');
                loadingLi.style.padding = '10px 14px';
                loadingLi.style.fontSize = '13px';
                loadingLi.style.color = '#64748b';
                loadingLi.textContent = 'Buscando direcciones...';
                searchResultsList.innerHTML = '';
                searchResultsList.appendChild(loadingLi);
                searchResultsList.style.display = 'block';

                const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query.trim())}&addressdetails=1&limit=5&accept-language=es`;

                fetch(url, {
                    headers: { 'Accept': 'application/json' }
                })
                .then(function(res) {
                    if (!res.ok) throw new Error('Error en búsqueda de direcciones');
                    return res.json();
                })
                .then(function(results) {
                    searchResultsList.innerHTML = '';
                    if (!results || results.length === 0) {
                        const emptyLi = document.createElement('li');
                        emptyLi.style.padding = '10px 14px';
                        emptyLi.style.fontSize = '13px';
                        emptyLi.style.color = '#64748b';
                        emptyLi.textContent = 'No se encontraron resultados para esa búsqueda.';
                        searchResultsList.appendChild(emptyLi);
                        return;
                    }

                    results.forEach(function(item) {
                        const li = document.createElement('li');
                        li.className = 'nominatim-result-item';
                        li.style.padding = '10px 14px';
                        li.style.cursor = 'pointer';
                        li.style.borderBottom = '1px solid #f1f5f9';
                        li.style.fontSize = '13px';
                        li.style.display = 'flex';
                        li.style.alignItems = 'flex-start';
                        li.style.gap = '8px';
                        li.style.transition = 'background .15s ease';

                        li.innerHTML = `
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="flex-shrink:0; margin-top:2px;">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                                <circle cx="12" cy="10" r="3"></circle>
                            </svg>
                            <span style="color:#0f172a; line-height: 1.4;">${item.display_name}</span>
                        `;

                        li.addEventListener('mouseenter', function() {
                            li.style.background = '#f8fafc';
                        });
                        li.addEventListener('mouseleave', function() {
                            li.style.background = 'transparent';
                        });

                        li.addEventListener('mousedown', function(e) {
                            e.preventDefault();
                            inputSearch.value = item.display_name;
                            fillFieldsFromNominatim(item, true);
                            hideResults();
                        });

                        searchResultsList.appendChild(li);
                    });
                })
                .catch(function(err) {
                    searchResultsList.innerHTML = '';
                    const errorLi = document.createElement('li');
                    errorLi.style.padding = '10px 14px';
                    errorLi.style.fontSize = '13px';
                    errorLi.style.color = '#ef4444';
                    errorLi.textContent = 'Error al consultar el servicio de búsqueda. Podés marcar directamente en el mapa.';
                    searchResultsList.appendChild(errorLi);
                    console.warn('Nominatim search error:', err);
                });
            }

            inputSearch.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                const query = this.value;
                debounceTimer = setTimeout(function() {
                    searchNominatim(query);
                }, 600);
            });

            inputSearch.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    clearTimeout(debounceTimer);
                    searchNominatim(this.value);
                } else if (e.key === 'Escape') {
                    hideResults();
                }
            });

            document.addEventListener('click', function(e) {
                if (!inputSearch.contains(e.target) && !searchResultsList.contains(e.target)) {
                    hideResults();
                }
            });
        }
    }

    // Exponer globalmente
    window.initHotelMapPicker = initHotelMapPicker;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHotelMapPicker);
    } else {
        initHotelMapPicker();
    }
})();
