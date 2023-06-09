import logging

from gui.widgets.graphWidgetUi import GraphsUi
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
import numpy as np
from collections import deque
import pyqtgraph as pg

log = logging.getLogger(__name__)


class GraphsWidget(QFrame, GraphsUi):

    def __init__(self, context, signals):
        super(GraphsWidget, self).__init__()
        self.signals = signals
        self.context = context
        self.setupUi(self)
        self.display_time = self.context.display_time
        self.refresh_rate = self.context.refresh_rate
        self.num_points = self.display_time * self.refresh_rate
        self.x_axis = list(np.linspace(-self.display_time, 0, self.num_points))
        self.y_diff = deque([np.nan for _ in range(self.num_points)])
        self.y_i0 = deque([np.nan for _ in range(self.num_points)])
        self.y_ratio = deque([np.nan for _ in range(self.num_points)])
        self.y_ave = deque([np.nan for _ in range(self.num_points)])
        self.old_vals_diff = deque([], 2000)
        self.old_vals_i0 = deque([], 2000)
        self.old_vals_ratio = deque([], 2000)
        self.old_ave = deque([], 2000)
        self.diff_low_range = [np.nan for _ in range(self.num_points)]
        self.diff_high_range = [np.nan for _ in range(self.num_points)]
        self.diff_mean = [np.nan for _ in range(self.num_points)]
        self.i0_low_range = [np.nan for _ in range(self.num_points)]
        self.i0_high_range = [np.nan for _ in range(self.num_points)]
        self.i0_mean = [np.nan for _ in range(self.num_points)]
        self.ratio_low_range = [np.nan for _ in range(self.num_points)]
        self.ratio_high_range = [np.nan for _ in range(self.num_points)]
        self.ratio_mean = [np.nan for _ in range(self.num_points)]
        self.line_diff = self.graph1.plot(self.x_axis, list(self.y_diff), pen=None, symbol='o')
        self.line_i0 = self.graph2.plot(self.x_axis, list(self.y_i0), pen=None, symbol='o')
        self.line_ratio = self.graph3.plot(self.x_axis, list(self.y_ratio), pen=None, symbol='o')
        self.line_diff_low = self.graph1.plot(self.x_axis, list(self.diff_low_range),
                                              pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                              size=1, style=Qt.DashLine)
        self.line_diff_high = self.graph1.plot(self.x_axis, list(self.diff_high_range),
                                               pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                               size=1, style=Qt.DashLine)
        self.line_diff_mean = self.graph1.plot(self.x_axis, list(self.diff_mean),
                                               pen=pg.mkPen(width=1, color=(255, 165, 0)), size=1)
        self.line_i0_low = self.graph2.plot(self.x_axis, list(self.i0_low_range),
                                            pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                            size=1, style=Qt.DashLine)
        self.line_i0_high = self.graph2.plot(self.x_axis, list(self.i0_high_range),
                                             pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                             size=1, style=Qt.DashLine)
        self.line_i0_mean = self.graph2.plot(self.x_axis, list(self.i0_mean),
                                             pen=pg.mkPen(width=1, color=(255, 165, 0)), size=1)
        self.line_ratio_low = self.graph3.plot(self.x_axis, list(self.ratio_low_range),
                                               pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                               size=1, style=Qt.DashLine)
        self.line_ratio_high = self.graph3.plot(self.x_axis, list(self.ratio_high_range),
                                                pen=pg.mkPen(width=1, color=(255, 255, 0)),
                                                size=1, style=Qt.DashLine)
        self.line_ratio_mean = self.graph3.plot(self.x_axis, list(self.ratio_mean),
                                                pen=pg.mkPen(width=1, color=(255, 165, 0)), size=1)
        self.line_ave = self.graph3.plot(self.x_axis, list(self.y_ave))
        self.calibration_values = {}
        self.calibrated = False
        self.connect_signals()

    def connect_signals(self):
        # connect signals
        self.signals.refreshGraphs.connect(self.plot_data)
        self.signals.changeCalibrationValues.connect(self.update_calibration_values)
        self.signals.changeDisplayTime.connect(self.set_display_time)
        self.signals.setNewXAxis.connect(self.set_new_axis)

    def update_calibration_values(self, cal):
        self.calibration_values = cal
        self.calibrated = True
        self.calibrate()

    def calibrate(self):
        length = len(self.x_axis)
        self.diff_low_range = list(
            [self.calibration_values['diff']['range'][0]]*length)
        self.diff_high_range = list(
            [self.calibration_values['diff']['range'][1]]*length)
        self.diff_mean = list(
            [self.calibration_values['diff']['mean']]*length)
        self.i0_low_range = list(
            [self.calibration_values['i0']['range'][0]] * length)
        self.i0_high_range = list(
            [self.calibration_values['i0']['range'][1]] * length)
        self.i0_mean = list([self.calibration_values['i0']['mean']] * length)
        self.ratio_low_range = list(
            [self.calibration_values['ratio']['range'][0]] * length)
        self.ratio_high_range = list(
            [self.calibration_values['ratio']['range'][1]] * length)
        self.ratio_mean = list(
            [self.calibration_values['ratio']['mean']] * length)
        self.plot_calibration()

    def plot_data(self, buf: dict, count: int):
        """
        Manage data deques for plot displays.

        Parameters:
        ----------
        buf : (dict) Dictionary of types of data to display.
        count : (int) Count of data points.
        """
        old_diff = self.y_diff.popleft()
        old_i0 = self.y_i0.popleft()
        old_ratio = self.y_ratio.popleft()

        if count == int(self.num_points):
            self.old_vals_diff.append(old_diff)
            self.old_vals_i0.append(old_i0)
            self.old_vals_ratio.append(old_ratio)

        self.y_diff.append(buf['diff'])
        self.y_i0.append(buf['i0'])
        self.y_ratio.append(buf['ratio'][-2])

        self.line_diff.setData(self.x_axis, list(self.y_diff))
        self.line_i0.setData(self.x_axis, list(self.y_i0))
        self.line_ratio.setData(self.x_axis, list(self.y_ratio))


    def plot_calibration(self):
        self.line_diff_low.setData(self.x_axis, self.diff_low_range)
        self.line_diff_high.setData(self.x_axis, self.diff_high_range)
        self.line_diff_mean.setData(self.x_axis, self.diff_mean)
        self.line_i0_low.setData(self.x_axis, self.i0_low_range)
        self.line_i0_high.setData(self.x_axis, self.i0_low_range)
        self.line_i0_mean.setData(self.x_axis, self.i0_mean)
        self.line_ratio_low.setData(self.x_axis, self.ratio_low_range)
        self.line_ratio_high.setData(self.x_axis, self.ratio_high_range)
        self.line_ratio_mean.setData(self.x_axis, self.ratio_mean)

    def set_display_time(self, t: int, rr: int):
        """
        Update display ranges for main window plots.

        Based on user input for the number of seconds to display
        and the data refresh rate, change the data points shown in
        the plots of the main window.

        Parameters:
        ----------
        t : (int) Number of seconds of data to show.
        rr : (int) New refresh rate.
        """
        old_num_points = self.num_points
        new_display_time = int(t)
        new_rr = int(rr)
        new_num_points = int(new_display_time * new_rr)

        y_diff: deque = deque([])
        y_i0: deque = deque([])
        y_ratio: deque = deque([])

        time_diff: int = new_display_time - self.display_time
        rate_diff: int = new_rr - self.refresh_rate
        pts_diff: int = np.abs(new_num_points - self.num_points)

        if not rate_diff:
            # Refresh rate the same -> start from existing data points
            y_diff.extend(self.y_diff)
            y_i0.extend(self.y_i0)
            y_ratio.extend(self.y_ratio)

            if time_diff > 0:
                # Append data points from the "old pts" deque if too short
                while pts_diff > 0 and len(self.old_vals_diff) > 0:
                    y_diff.appendleft(self.old_vals_diff.pop())
                    y_i0.appendleft(self.old_vals_i0.pop())
                    y_ratio.appendleft(self.old_vals_ratio.pop())
                    pts_diff -= 1

                remaining_pts: int = new_num_points - len(y_diff)
                y_diff.extendleft([np.nan for _ in range(remaining_pts)])
                y_i0.extendleft([np.nan for _ in range(remaining_pts)])
                y_ratio.extendleft([np.nan for _ in range(remaining_pts)])

            else:
                # Cache points in the "old pts" deque if too long
                while pts_diff > 0:
                    self.old_vals_diff.append(y_diff.popleft())
                    self.old_vals_i0.append(y_i0.popleft())
                    self.old_vals_ratio.append(y_ratio.popleft())
                    pts_diff -= 1
        else:
            # Refresh rate changed -> create "empty" deque of nan
            pts_range: range = range(new_num_points)
            y_diff.extend([np.nan for _ in pts_range])
            y_i0.extend([np.nan for _ in pts_range])
            y_ratio.extend([np.nan for _ in pts_range])
            self.old_vals_diff = deque([], 2000)
            self.old_vals_i0 = deque([], 2000)
            self.old_vals_ratio = deque([], 2000)


        self.signals.setNewXAxis.emit(0)
        self.y_diff = y_diff
        self.y_i0 = y_i0
        self.y_ratio = y_ratio

    def set_new_axis(self, idx):
        self.display_time = self.context.display_time
        self.refresh_rate = self.context.refresh_rate
        self.num_points = self.display_time * self.refresh_rate
        self.x_axis = list(np.linspace(-self.display_time, 0, self.num_points))
        if self.calibrated:
            self.calibrate()
