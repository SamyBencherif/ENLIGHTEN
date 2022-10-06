import logging

from . import common
from .ScrollStealFilter import ScrollStealFilter

log = logging.getLogger(__name__)

##
# This class is not yet fully refactored.
class PageNavigation:

    def __init__(self,
            graph,
            marquee,
            multispec,
            save_options,
            stylesheets,

            combo_view,
            button_raman,
            button_non_raman,
            button_expert,
            stack_hardware,
            stack_main,

            update_feature_visibility,
            scroll_area,
            textEdit_log,                       # todo move to LoggingFeature
            frame_transmission_options,         # todo move to TransmissionFeature
            sfu,
            ):

        self.graph              = graph
        self.marquee            = marquee
        self.multispec          = multispec
        self.save_options       = save_options
        self.stylesheets        = stylesheets
        self.sfu                = sfu
                                
        self.button_raman       = button_raman
        self.button_non_raman   = button_non_raman
        self.button_expert      = button_expert
        self.combo_view         = combo_view
        self.stack_hardware     = stack_hardware 
        self.stack_main         = stack_main 
        self.combo_technique    = self.sfu.technique_comboBox
        self.combo_technique.installEventFilter(ScrollStealFilter(self.combo_technique))

        self.frame_transmission_options = frame_transmission_options 
        self.update_feature_visibility = update_feature_visibility
        self.scroll_area = scroll_area
        self.textEdit_log = textEdit_log

        self.operation_mode = common.OperationModes.RAMAN
        self.current_view = common.Views.SCOPE
        self.has_used_raman = False
        self.current_technique = self.sfu.technique_comboBox.currentIndex()

        self.button_raman           .clicked            .connect(self.set_operation_mode_raman)
        self.button_non_raman       .clicked            .connect(self.set_operation_mode_non_raman)
        self.button_expert          .clicked            .connect(self.set_operation_mode_expert)
        self.combo_view             .currentIndexChanged.connect(self.update_view_callback)
        self.combo_technique        .currentIndexChanged.connect(self.update_technique_callback)

    def post_init(self):
        self.set_view_scope()
        self.sfu.frame_hardware_capture_control_cb.hide()
        self.sfu.label_hardware_capture_control.hide()
        self.set_operation_mode_non_raman()
        self.frame_transmission_options.hide()

    # ##########################################################################
    # activity introspection
    # ##########################################################################

    def doing_scope_capture     (self): return self.get_main_page() == common.Pages.SPEC_CAPTURE
    def doing_hardware_capture  (self): return self.current_view == common.Views.FACTORY
    def doing_settings          (self): return self.current_view == common.Views.SETTINGS
    def doing_hardware          (self): return self.current_view == common.Views.HARDWARE
    def doing_scope             (self): return self.current_view == common.Views.SCOPE
    def doing_log               (self): return self.current_view == common.Views.LOG

    def get_current_view(self): 
        return self.current_view

    def get_current_view_name(self):
        return common.ViewsHelper.get_pretty_name(self.current_view)

    # ##########################################################################
    # Views
    # ##########################################################################

    # parameterized method provided for constructor; otherwise we use named
    # functions which better support callbacks
    def set_view(self, view):
        if view == common.Views.HARDWARE     : return self.set_view_hardware()
        if view == common.Views.SCOPE        : return self.set_view_scope()

        log.error("set_view: Unsupported view: %s", view)
        self.set_view_scope()

    def update_technique_callback(self):
        self.current_technique = self.sfu.technique_comboBox.currentIndex()
        if self.current_technique == common.Techniques.EMISSION:
            self.frame_transmission_options.hide()
        elif self.current_technique == common.Techniques.ABSORBANCE:
            self.frame_transmission_options.hide()
            self.set_technique_absorbance()
        elif self.current_technique == common.Techniques.TRANSMISSION:
            self.frame_transmission_options.show()
            self.set_technique_transmission

    def set_technique_raman(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not spec.settings.has_excitation():
            self.marquee.error("Raman mode requires an excitation wavelength")
            return self.set_operation_mode_non_raman()

        self.set_technique_common(common.Techniques.EMISSION)
        self.graph.set_x_axis(common.Axes.WAVENUMBERS)
        self.graph.set_y_axis(common.Axes.COUNTS)

        # Per Dieter, Raman mode should default to APLS. Note that we don't
        # currently track settings (baseline correction, integration time, laser
        # enable etc) by technique, so baseline correction will REMAIN selected
        # if you change to Scope or Absorbance/etc...
        if not self.has_used_raman:
            self.has_used_raman = True
            self.save_options.force_wavenumber()
            if spec.app_state.has_dark() and not spec.app_state.baseline_correction_enabled:
                # persist this because we don't know how long they'll stay on the
                # Scope Setup screen
                #
                # Dieter says "not yet"
                #
                # self.marquee.info("Auto-enabling baseline correction", persist=True)
                # self.baseline_correction.reset(enable=True)
                pass

    # called whenever the user changes the view via the GUI combobox
    def update_view_callback(self):
        self.current_view = self.determine_current_view()
        log.debug("update_view_callback: current_view now %d", self.current_view)

        if self.doing_hardware():
            self.sfu.frame_hardware_capture_control_cb.show()
            self.sfu.label_hardware_capture_control.show()
        else:
            self.sfu.frame_hardware_capture_control_cb.hide()
            self.sfu.label_hardware_capture_control.hide()

        if self.doing_hardware()        : return self.set_view_hardware()
        if self.doing_hardware_capture(): return self.set_view_hardware_capture()
        if self.doing_settings()        : return self.set_view_settings()
        if self.doing_scope()           : return self.set_view_scope()
        if self.doing_raman()           : return self.set_view_raman()
        if self.doing_log()             : return self.set_view_logging()
        if self.doing_transmission()    : return self.set_view_transmission()
        if self.doing_absorbance()      : return self.set_view_absorbance()
        
        log.error("update_view_callback: unknown view: %s", self.current_view)
        self.set_view_scope()

    def toggle_hardware_and_scope(self):
        if self.doing_hardware():
            self.set_view_scope()
        else:
            self.set_view_hardware()

    def set_view_settings(self):
        self.set_view_common(common.Views.SETTINGS)
        self.set_main_page(common.Pages.SPEC_SETTINGS)

    def set_view_logging(self):
        log.info("setting view to hardware")
        self.set_view_common(common.Views.HARDWARE)
        self.stack_hardware.setCurrentIndex(1)
        self.set_main_page(common.Pages.HARDWARE_SETTINGS)

    def set_view_hardware(self):
        log.info("setting view to hardware")
        self.set_view_common(common.Views.HARDWARE)
        self.stack_hardware.setCurrentIndex(0)
        self.set_main_page(common.Pages.HARDWARE_SETTINGS)

    def set_view_hardware_capture(self):
        log.info("setting view to hardware capture")
        self.set_view_common(common.Views.HARDWARE)
        self.set_main_page(common.Pages.HARDWARE_CAPTURE)

    def set_view_scope(self):
        self.set_view_common(common.Views.SCOPE)
        self.set_main_page(common.Pages.SPEC_CAPTURE)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.COUNTS)

    def set_view_raman(self):
        spec = self.multispec.current_spectrometer()
        if spec is None or not spec.settings.has_excitation():
            self.marquee.error("Raman mode requires an excitation wavelength")
            return self.set_view_scope()

        self.graph.set_x_axis(common.Axes.WAVENUMBERS)
        self.graph.set_y_axis(common.Axes.COUNTS)

        # Per Dieter, Raman mode should default to APLS. Note that we don't
        # currently track settings (baseline correction, integration time, laser
        # enable etc) by view, so baseline correction will REMAIN selected
        # if you change to Scope or Absorbance/etc...
        if not self.has_used_raman:
            self.has_used_raman = True
            self.save_options.force_wavenumber()
            if spec.app_state.has_dark() and not spec.app_state.baseline_correction_enabled:
                # persist this because we don't know how long they'll stay on the
                # Scope Setup screen
                #
                # Dieter says "not yet"
                #
                # self.marquee.info("Auto-enabling baseline correction", persist=True)
                # self.baseline_correction.reset(enable=True)
                pass

    def set_view_transmission(self):
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.PERCENT)

    def set_view_absorbance(self):
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.AU)

    def set_view_common(self, view):
        log.debug("set_view_common: view %d", view)
        #self.frame_transmission_options.setVisible(self.using_transmission())

        self.graph.reset_axes()

        # Business Objects
        self.update_feature_visibility()

    # ##########################################################################
    # Page Navigation: Operation Mode
    # ##########################################################################

    def set_hardware_details_active(self):
        self.stack_hardware.setCurrentIndex(0)
        self.stylesheets.apply(self.button_details, "tab_active")
        self.stylesheets.apply(self.button_logging, "tab_inactive")

    def set_hardware_logging_active(self):
        self.stack_hardware.setCurrentIndex(1)
        self.stylesheets.apply(self.button_details, "tab_inactive")
        self.stylesheets.apply(self.button_logging, "tab_active")

        self.scroll_to_top(self.scroll_area)
        self.scroll_to_top(self.textEdit_log)

    def scroll_to_top(self, widget):
        widget.verticalScrollBar().setValue(widget.verticalScrollBar().minimum())
        
    def set_main_page(self, page):
        log.debug(f"setting main page to index {page}")
        self.stack_main.setCurrentIndex(page)

    def get_main_page(self):
        return self.stack_main.currentIndex()

    def doing_transmission      (self): return self.current_technique == common.Techniques.TRANSMISSION
    def doing_absorbance        (self): return self.current_technique == common.Techniques.ABSORBANCE
    def using_transmission      (self): return self.current_technique in [ common.Techniques.TRANSMISSION, common.Techniques.ABSORBANCE ]
    def using_reference         (self): return self.current_technique in [ common.Techniques.TRANSMISSION, common.Techniques.ABSORBANCE ]

    def doing_raman(self):
        return self.operation_mode == common.OperationModes.RAMAN

    def is_expert(self):
        return self.operation_mode == common.OperationModes.EXPERT

    def set_technique_absorbance(self):
        self.set_technique_common(common.Techniques.ABSORBANCE)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.AU)

    def set_technique_transmission(self):
        self.set_technique_common(common.Techniques.TRANSMISSION)
        self.graph.set_x_axis(common.Axes.WAVELENGTHS)
        self.graph.set_y_axis(common.Axes.PERCENT)

    def set_technique_common(self, technique):
        log.debug("set_technique_common: technique %d", technique)
        self.combo_technique.setCurrentIndex(technique)
        self.frame_transmission_options.setVisible(self.using_transmission())

        self.graph.reset_axes()

        # Business Objects
        self.update_feature_visibility()
    
    def set_operation_mode_raman(self):
        log.debug(f"raman mode operation set")
        self.stylesheets.apply(self.button_raman, "left_rounded_active")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.stylesheets.apply(self.button_expert, "right_rounded_inactive")
        self.operation_mode = common.OperationModes.RAMAN
        self.update_feature_visibility()
        self.hide_non_raman_technqiue()

    def set_operation_mode_non_raman(self):
        self.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_active")
        self.stylesheets.apply(self.button_expert, "right_rounded_inactive")
        self.operation_mode = common.OperationModes.NON_RAMAN
        self.update_feature_visibility()
        self.display_non_raman_technqiue()
        self.frame_transmission_options.hide()

    def set_operation_mode_expert(self):
        self.stylesheets.apply(self.button_raman, "left_rounded_inactive")
        self.stylesheets.apply(self.button_non_raman, "center_rounded_inactive")
        self.stylesheets.apply(self.button_expert, "right_rounded_active")
        self.operation_mode = common.OperationModes.EXPERT
        self.update_feature_visibility()
        self.display_non_raman_technqiue()

    def set_operation_mode(self, mode):
        if mode == common.OperationModes.SETUP  : return self.set_operation_mode_setup()
        if mode == common.OperationModes.CAPTURE: return self.set_operation_mode_capture()

        log.error("Unsupported operation mode: %s", mode)
        self.set_operation_mode_capture()

    def set_operation_mode_common(self, mode):
        # cache the newly-set operation mode for the current view, so the
        # next time we switch back to this view we'll restore this mode
        self.view_operation_mode[self.current_view] = mode

        # This is used by doing_peakfinding()...generally setting operation mode
        # is fire-and-forget, but that's one case when we later want to
        # introspect and know what mode we're supposedly in.
        self.operation_mode = mode

        # All connected spectrometers always share the same view.  It's a
        # valid question if view should then be stored in app_state, since
        # it's not really a per-spectrometer attribute, but adding for
        # consistency and convenience.
        self.multispec.set_app_state("view_name", self.get_current_view_name(), all=True)

    def display_non_raman_technqiue(self):
        self.sfu.technqiueWidget_label.show()
        self.sfu.techniqueWidget_shaded.show()

    def hide_non_raman_technqiue(self):
        self.sfu.technqiueWidget_label.hide()
        self.sfu.techniqueWidget_shaded.hide()

    def determine_current_view(self):
        label = self.combo_view.currentText().lower()

        if label == "hardware": return common.Views.HARDWARE
        if label == "scope":    return common.Views.SCOPE
        if label == "settings": return common.Views.SETTINGS
        if label == "log":      return common.Views.LOG
        if label == "factory":  return common.Views.FACTORY

        log.error("unknown view %s", label)
        return common.Views.HARDWARE
