import os
import logging
import datetime

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class SaveAsAngstrom(EnlightenPluginBase):
    """
    This writes received spectra into a custom folder with a different
    file format than ENLIGHTEN (specifically, wavelength in Ångstrom and
    ABSOLUTE wavenumber (as opposed to "Raman shift in wavenumbers").

    This is demonstrating how a plug-in can register for ENLIGHTEN events
    (in this case, "save").

    Note we are currently using the 'event' registration service provided
    by the plugin architecture, and not registering directly with 
    self.ctl.measurements.MeasurementFactory. That would work too, but 
    we'd need to be careful to unregister when the plugin was unloaded.
    """

    def get_configuration(self):
        self.name = "Save As Å/cm⁻¹"

        # register for save events via the plugin architecture
        self.events = { "save": self.save_measurement }
        
        # e.g. C:\Users\mzieg\Documents\EnlightenSpectra\SaveAsAngstrom
        self.directory = os.path.join(self.ctl.save_options.get_directory(), "SaveAsAngstrom")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def save_measurement(self, measurement):
        """
        This callback receives new enlighten.Measurement objects generated by 
        MeasurementFactory.
        """
        pr = measurement.processed_reading
        settings = measurement.spec.settings

        # deliberately use a slightly different naming nomenclature than ENLIGHTEN, 
        # to show we can
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        filename = f"{settings.eeprom.serial_number}-{timestamp}-angstrom.csv"
        pathname = os.path.join(self.directory, filename)

        log.info(f"saving {pathname}")
        with open(pathname, 'w', encoding="utf-8") as f:
            f.write('pixel, angstrom (A), absolute wavenumber (1/cm), intensity\n')
            for i in range(len(pr.processed)):
                nm = settings.wavelengths[i]
                angstrom = 10.0 * nm
                absolute_wavenumber = 1.0 / (nm / 1e7) # NOT Raman shift!
                f.write("%04d, %.5e, %.2f, %.3f\n" % (i, angstrom, absolute_wavenumber, pr.processed[i]))
