import requests


# https://gis.chesapeakebay.net/ags/rest/services/geotagging/nad83/MapServer/identify?geometry=-76.3922220000%2C37.2172200000&geometryType=esriGeometryPoint&sr=&layers=all&layerDefs=&time=&layerTimeOptions=&tolerance=0&mapExtent=-80.553838%2C37.018329%2C-76.1%2C42.5&imageDisplay=2000%2C2000%2C96&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&dynamicLayers=&returnZ=false&returnM=false&gdbVersion=&f=pjson

class ChesapeakeBayIntegration:
    url = 'https://gis.chesapeakebay.net/ags/rest/services/geotagging/nad83/MapServer/identify'

    static_params = {
        # 'geometry': '-76.3922220000,37.2172200000',
        # 'geometry': '-77.1810400000,40.2079200000,
        'geometryType': 'esriGeometryPoint',
        # 'sr': '',
        'layers': 'all',
        # 'layerDefs': '',
        # 'time': '',
        # 'layerTimeOptions': '',
        'tolerance': 0,
        'mapExtent': '-80.553838,37.018329,-76.1,42.5',
        'imageDisplay': '2000,2000,96',
        'returnGeometry': 'false',
        # 'maxAllowableOffset': '',
        # 'geometryPrecision': '',
        # 'dynamicLayers': '',
        'returnZ': 'false',
        'returnM': 'false',
        # 'gdbVersion': '',
        'f': 'pjson'
    }

    def get(self, lat, lon):
        params = {**self.static_params, **{'geometry': lon + ',' + lat}}

        resp = requests.get(self.url, params)

        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'results' not in data:
                    return None

                results = data['results']

                if len(results) == 0:
                    return None

                huc12 = None
                fallLine = None
                fips = None
                cbseg = None

                for layer in results:
                    if 'layerName' in layer:
                        if layer['layerName'] == 'HUC12':
                            if 'attributes' in layer:
                                huc12 = layer['attributes']
                        elif layer['layerName'] == 'Fall_line':
                            if 'value' in layer:
                                fallLine = layer['value']
                        elif layer['layerName'] == 'FIPS':
                            if 'attributes' in layer:
                                fips = layer['attributes']
                        elif layer['layerName'] == 'CBSEG_2003':
                            if 'value' in layer:
                                cbseg = layer['value']

                # make sure all of our data got set
                # if huc12 is None or fallLine is None or fips is None or cbseg is None:
                #     return None

                # return values mapped to db cols
                return {
                    'Huc12': huc12['HUC_12'] if huc12 is not None and 'HUC_12' in huc12 else None,
                    'WaterBody': huc12['HUC_12_NAME'] if huc12 is not None and 'HUC_12_NAME' in huc12 else None,
                    'Huc6Name': huc12['HUC_6_NAME'] if huc12 is not None and 'HUC_6_NAME' in huc12 else None,
                    'Tidal': True if fallLine == 'below' else False,
                    'Fips': fips['FIPS'] if fips is not None and 'FIPS' in fips else None,
                    'CityCounty': fips['CoNameFull'] if fips is not None and 'CoNameFull' in fips else None,
                    'State': fips['StName'] if fips is not None and 'StName' in fips else None,
                    'Cbseg': cbseg
                }

            except Exception as err:
                print('Chesapeake Bay API resp error: ' + str(err))
                return None

        # invalid response
        return None


