import os
import logging

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginField,    \
                            EnlightenPluginResponse,  \
                            EnlightenPluginDependency, \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

##
# A simple plug-in to add emission lines from standard gas lamps to the current 
# spectra.  The lines displayed are limited to those appearing within the current
# spectrometer's configured wavelength calibration.  Lines are scaled to the 
# current spectrum, and relative intensities are roughly set to approximate
# typical appearance.
class EmissionLines(EnlightenPluginBase):

    MIN_REL_INTENSITY = 0.2

    def __init__(self):
        super().__init__()
        self.lamps = self.get_lamps()

    def get_configuration(self):
        fields = []

        # These would be better as a single drop-down combo box, but we haven't 
        # yet added that as a supported plugin input type.
        for lamp in self.lamps:
            fields.append(EnlightenPluginField(name=lamp, direction="input", datatype=bool, initial=False))
        return EnlightenPluginConfiguration(
            name            = "EmissionLines", 
            series_names    = sorted(self.lamps.keys()),
            fields          = fields)

    def connect(self, enlighten_info):
        super().connect(enlighten_info)
        return True

    def disconnect(self):
        super().disconnect()

    def process_request(self, request):
        pr = request.processed_reading
        settings = request.settings

        series_data = {}
        for lamp in self.lamps:
            if request.fields[lamp]:
                series_data[lamp] = self.generate_series(lamp=lamp, wavelengths=settings.wavelengths, spectrum=pr.processed)

        return EnlightenPluginResponse(request=request, series=series_data)      

    ## 
    # Generate a synthetic spectrum, bounded in x to match the specified x-axis 
    # in wavelengths, bounded in y to match the min/max of the specified 
    # spectrum, of the specified lamp's emission lines.
    def generate_series(self, lamp, wavelengths, spectrum):
        
        # determine the vertical extent of the synthetic spectrum
        lo = min(spectrum)
        hi = max(spectrum)

        # determine which of this lamp's emission lines to visualize on the graph
        lines = self.lamps[lamp]
        visible = []
        max_rel_intensity = self.MIN_REL_INTENSITY
        for peak in sorted(lines.keys()):
            rel_intensity = lines[peak]
            if peak >= wavelengths[0] and peak <= wavelengths[-1]:
                visible.append(peak)
                max_rel_intensity = max(max_rel_intensity, rel_intensity)

        series_x = [ wavelengths[0] ]
        series_y = [ lo ]

        log.debug(f"displaying {len(visible)} {lamp} peaks")
        for x in visible:
            rel_intensity = max(lines[x], self.MIN_REL_INTENSITY)
            y = lo + (hi - lo) * rel_intensity / max_rel_intensity
            series_x.extend((x - 0.1,  x, x + 0.1))
            series_y.extend((lo,       y,      lo))

        series_x.append(wavelengths[-1])
        series_y.append(lo)

        return { "x": series_x, "y": series_y }

    ## 
    # Emission lines with relative intensities of 0 appear in literature, but are
    # either unverified or hard to see with our spectrometers in empirical usage.
    #
    # Relative intensity will realistically vary by model, but these values are a
    # reasonable starting point.
    #
    # @todo for completeness add He, Rn
    #
    # @par Sources
    # 
    # Data taken from NIST, as well as vendor websites of calibration lamps.
    #
    # @see https://physics.nist.gov/PhysRefData/ASD/lines_form.html
    #
    # Ar:
    # @see http://oceanoptics.com/wp-content/uploads/AR-1_spectra-01.jpg
    # @see http://bwtek.com/wp-content/uploads/2012/05/scl100_ar.jpg
    #
    # Hg:
    # @see http://oceanoptics.com/wp-content/uploads/HG-1-spectrum-with-USB2000-XR1-2.png
    # @see http://bwtek.com/wp-content/uploads/2012/05/scl100_mer.jpg
    #
    # Kr:
    # @see http://oceanoptics.com/wp-content/uploads/KR-1-spectral-range-web.jpg
    # @see http://bwtek.com/wp-content/uploads/2012/05/scl100_kr.jpg
    # 
    # Ne:
    # @see http://oceanoptics.com/wp-content/uploads/NE-1-spectral-range-web.jpg
    # @see http://bwtek.com/wp-content/uploads/2012/05/scl100_neon.jpg
    #
    # Xe:
    # @see http://oceanoptics.com/wp-content/uploads/XE-1_spectra-01.jpg
    def get_lamps(self):
        return {
            "Ar": {
                 696.543: 1,
                 706.722: .5,
                 794.818: 1,
                 800.616: 1,
                 801.479: 1,
                 810.369: 2,
                 811.531: 4,
                 826.452: 3,
                 840.821: 3,
                 842.465: 5,
                 852.144: 2,
                 866.794: 1,
                 876.058: 0,
                 879.947: 0,
                 894.310: 0,
                 912.297: 9,
                 922.450: 2,
                 935.422: 0,
                 965.779: 1,
                 978.450: 0,
                1047.005: 0,
                1066.660: 0,
                1110.646: 0,
                1148.811: 0,
                1166.871: 0,
                1171.949: 0,
                1211.233: 0,
                1213.974: 0,
                1234.339: 0,
                1240.283: 0,
                1243.932: 0,
                1248.766: 0,
                1270.288: 0,
                1273.342: 0,
                1280.274: 0,
                1295.666: 0,
                1300.826: 0,
                1322.811: 0,
                1327.264: 0,
                1331.321: 0,
                1336.711: 0,
                1350.419: 0,
                1362.266: 0,
                1367.855: 0,
                1371.858: 0,
                1382.572: 0,
                1390.748: 0,
                1409.364: 0,
                1504.650: 0,
                1517.269: 0,
                1532.934: 0,
                1598.949: 0,
                1694.058: 0,
                1704.288: 0,
            },
            "Hg": {
                 253.652: 0,
                 296.728: 0,
                 302.150: 0,
                 313.155: 0,
                 334.148: 0,
                 365.015: 0,
                 404.656: 1,
                 435.833: 1,
                 546.074: 5,
                 576.960: 1,
                 579.066: 1,
                 696.543: 1,
                 706.722: 1,
                 714.704: 1,
                 727.294: 1,
                 738.398: 1,
                 750.387: 2,
                 763.511: 5,
                 772.376: 2,
                 794.818: 1,
                 800.616: 2,
                 811.531: 4,
                 826.452: 3,
                 842.465: 3,
                 852.144: 1,
                 866.794: 1,
                 912.297: 5,
                 922.450: 1,
                 965.779: 1,
                 978.450: 1,
                1013.976: 1,
            },
            "Kr":  {  
                 427.397: 2,
                 428.297: .5,
                 431.958: 3,
                 436.264: .5,
                 437.612: 1,
                 439.997: 1,
                 445.392: .7,
                 446.369: 1.5,
                 450.235: 1,
                 556.222: 3.8,
                 557.029: 4,
                 587.092: 5,
                 758.741: 1,
                 760.155: 10,
                 768.525: 8,
                 769.454: 9,
                 785.482: 7,
                 791.343: 1,
                 805.950: 1,
                 810.437: 1,
                 811.290: 1,
                 819.006: 1,
                 826.324: 1,
                 829.811: 1,
                 850.887: 1,
                 877.675: 1,
                 892.869: 1,
                1181.938: 0,
                1220.353: 0,
                1317.741: 0,
                1363.422: 0,
                1442.679: 0,
                1473.444: 0,
                1520.310: 0,
                1537.204: 0,
                1620.872: 0,
                1689.044: 0,
                1755.350: 0,
                1785.738: 0,
                1800.223: 0,
                1816.732: 0,
            },
            "Ne": {
                 341.790: 0,
                 342.391: 0,
                 344.770: 0,
                 345.076: 0,
                 345.419: 0,
                 346.052: 0,
                 346.658: 0,
                 347.257: 0,
                 349.806: 0,
                 350.121: 0,
                 351.519: 0,
                 352.047: 0,
                 359.353: 0,
                 360.017: 0,
                 363.366: 0,
                 368.573: 0,
                 370.122: 0,
                 503.135: 0,
                 503.775: 0,
                 508.038: 0,
                 511.367: 0,
                 511.650: 0,
                 540.056: 1,
                 576.441: 1,
                 582.015: 1,
                 585.249: 2,
                 588.189: 1,
                 594.483: 2,
                 597.553: 1,
                 603.000: 1,
                 607.433: 2,
                 609.616: 3,
                 612.884: 1,
                 614.306: 4,
                 616.359: 2,
                 621.728: 2,
                 626.649: 3,
                 630.479: 2,
                 633.442: 3,
                 638.299: 5,
                 640.225: 6,
                 650.653: 4,
                 653.288: 3,
                 659.895: 3,
                 667.828: 4,
                 671.704: 2,
                 692.947: 3,
                 703.241: 5,
                 717.394: 1,
                 724.512: 4,
                 743.890: 2,
                 747.244: 1,
                 748.887: 1,
                 753.577: 1,
                 754.404: 1,
                 837.761: 0,
                 849.536: 0,
                 878.375: 0,
                1117.752: 0,
                1152.275: 0,
            },
            "Xe": {
                 452.186: 1,
                 462.420: 3,
                 466.849: 4,
                 469.097: 0,
                 469.804: 1,
                 473.415: 2,
                 479.262: 0,
                 480.702: 0,
                 482.971: 0,
                 484.329: 0,
                 491.651: 0,
                 492.315: 0,
                 733.930: 0,
                 738.600: 0,
                 739.379: 0,
                 740.040: 0,
                 755.979: 0,
                 758.468: 0,
                 764.391: 1,
                 780.265: 0,
                 788.132: 0,
                 796.734: 0,
                 805.726: 0,
                 806.134: 1,
                 823.163: 4,
                 826.652: 3,
                 828.012: 1,
                 834.680: .5,
                 840.920: .5,
                 881.941: 9,
                 895.230: 2,
                 904.545: 3,
                 916.265: 5,
                 979.970: 3,
                 992.319: 2,
                1083.837: 2,
                1262.339: 1,
                1365.706: 1,
                1414.244: 1,
                1473.281: 1,
                1541.839: 1,
                1605.328: 1,
                1647.290: 1,
                1656.023: 1,
                1672.815: 0,
                1763.882: 0,
                1790.450: 0,
                1809.090: 0,
                1832.530: 0,
                1959.940: 0,
                1984.638: 0,
            }
        }
