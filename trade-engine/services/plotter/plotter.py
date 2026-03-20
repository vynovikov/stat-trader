import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from config.config import Config
from domain.constants.constants import Constants
from domain.models.order import Order
from domain.types.candle import Candle
from domain.types.candle_action import CandleAction


class Plotter:
    def __init__(
        self,
        parent_dir: str,
        file_extension: str = ".png",
    ):

        self.parent_dir = parent_dir
        self.file_extension = file_extension
        self.type = "candle"
        self.style = "charles"
        self.up_candle_color = "white"
        self.down_candle_color = "black"
        self.edge_color = "black"
        self.wick_color = "black"
        self.volume_color = "in"
        self.face_color = "#fcfcfc"
        self.fig_color = "#ffffff"
        self.grid_color = "#cccccc"
        self.grid_style = "-"
        self.axes_edgecolor = "#cccccc"
        self.axes_linewidth = 0.8
        self.upper_name: str = "Price"
        self.lower_name: str = "Volume"
        self.entry_color = "grey"
        self.entry_width = 1
        self.entry_style = "--"
        self.entry_label = "Entry"
        self.finish_color = "grey"
        self.finish_width = 1
        self.finish_style = "--"
        self.finish_label = "Finish"
        self.sl_color = "red"
        self.sl_width = 1.5
        self.sl_style = "--"
        self.sl_label = "Stop Loss"
        self.legend_loc = "upper left"
        self.legend_fontsize = 9
        self.legend_frameon = True
        self.legend_framealpha = 0.8
        self.legend_facecolor = "white"
        self.legend_edgecolor = "lightgray"
        self.text_ha = 0.18
        self.text_va = 0.05
        self.text_fontsize = 12
        self.text_global_ha = "left"

        market_colors = mpf.make_marketcolors(
            up=self.up_candle_color,
            down=self.down_candle_color,
            edge=self.edge_color,
            wick=self.wick_color,
            volume=self.volume_color,
        )

        self.bw_gray_style = mpf.make_mpf_style(
            base_mpf_style=self.style,
            marketcolors=market_colors,
            facecolor=self.face_color,
            figcolor=self.fig_color,
            gridcolor=self.grid_color,
            gridstyle=self.grid_style,
            rc={
                "axes.edgecolor": self.axes_edgecolor,
                "axes.linewidth": self.axes_linewidth,
            },
        )

    def plot_full(
        self,
        candles: list[Candle],
        spread: float,
        order: Order,
        folder_name: str,
        file_name: str,
        reason: str = "SL triggered",
    ):

        mpl_df = self._compute_df(candles=candles)

        alines, acolor = self._compute_lines(candles=candles, order=order)

        description = self._title(order, reason)
        folder_name_final = ""
        suffix = self._path_suffix(order=order, reason=reason)

        if len(folder_name) > 0:
            folder_name_final = "_".join([folder_name, suffix])

        path = os.path.join(self.parent_dir, folder_name_final)
        os.makedirs(path, exist_ok=True)

        fig, axes = mpf.plot(
            data=mpl_df,
            type=self.type,
            style=self.bw_gray_style,
            volume=False,
            alines=dict(
                alines=alines,
                colors=acolor,
                linestyle="-",
                linewidths=2,
                alpha=0.8,
            ),
            title=description + f" | {candles[-1].close_time}",
            ylabel=self.upper_name,
            ylabel_lower=self.lower_name,
            returnfig=True,
            update_width_config={"candle_width": 0.35, "volume_width": 0.35},
        )

        ax = axes[0]

        finish_price = self._finish_price(order=order, candle=candles[-1])

        result_color = self._color(
            reason=reason, order=order, finish_price=finish_price
        )

        # Entry line
        ax.axhline(
            order.entry,
            color=self.entry_color,
            linestyle=self.entry_style,
            linewidth=self.entry_width,
            label=self.entry_label,
        )

        # Finish line
        if reason in {
            Constants.BUY_TP,
            Constants.BUY_LOSS,
            Constants.SELL_TP,
            Constants.SELL_LOSS,
        }:

            ax.axhline(
                finish_price,
                color=result_color,
                linestyle=self.finish_style,
                linewidth=self.finish_width,
                label=self.finish_label,
            )

        # Stop Loss line
        ax.axhline(
            order.sl,
            color=self.sl_color,
            linestyle=self.sl_style,
            linewidth=self.sl_width,
            label=self.sl_label,
        )

        entry_price = order.entry
        arrow_position = len(mpl_df.index) - 1

        # Vertical double-headed result arrow
        ax.annotate(
            "",
            xy=(arrow_position, entry_price),
            xytext=(arrow_position, finish_price),
            arrowprops=dict(
                arrowstyle="<->,head_width=0.3,head_length=0.3",
                color=result_color,
                lw=2.2,
                alpha=0.9,
            ),
            annotation_clip=False,
        )

        # Result amount text
        result = round(abs(order.entry - finish_price), 2)
        label = f"{result}"

        x_text = arrow_position + 0.10
        y_text = (entry_price + finish_price) / 2.0

        ax.text(
            x_text,
            y_text,
            label,
            va="center",
            ha="left",
            fontsize=9,
            color=result_color,
            bbox=dict(
                facecolor="white", alpha=0.7, boxstyle="round,pad=0.2", linewidth=0
            ),
            zorder=11,
        )

        # Lines legend
        ax.legend(
            loc=self.legend_loc,
            fontsize=self.legend_fontsize,
            frameon=self.legend_frameon,
            framealpha=self.legend_framealpha,
            facecolor=self.legend_facecolor,
            edgecolor=self.legend_edgecolor,
        )

        fig.savefig(
            os.path.join(path, "_".join([file_name, suffix])) + self.file_extension,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

    def _compute_lines(self, candles: list[Candle], order: Order) -> tuple[list, str]:
        if len(candles) < 2:
            raise ValueError("Not enough candles to plot order lines.")

        entry = order.entry
        left = candles[1].close_time + timedelta(minutes=5)
        right = candles[1].close_time + timedelta(minutes=10)
        acolor = "g" if order.action == CandleAction.BUY else "r"

        alines = [
            [(left, entry), (right, entry)],
        ]

        return alines, acolor

    def _compute_df(self, candles: list[Candle]) -> pd.DataFrame:
        raw = [c._asdict() for c in candles]
        df = pd.DataFrame(raw)
        mpl_df = df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        ).set_index(pd.to_datetime(df["close_time"]))[
            ["Open", "High", "Low", "Close", "Volume"]
        ]

        last_time = df["close_time"].iloc[-1]

        if isinstance(last_time, str):
            last_time = datetime.fromisoformat(last_time)

        next_time = last_time + timedelta(minutes=5)

        extra_row = pd.DataFrame(
            {
                "Open": [float("nan")],
                "High": [float("nan")],
                "Low": [float("nan")],
                "Close": [float("nan")],
                "Volume": [0],
            },
            index=[next_time],
        )

        mpl_df = pd.concat([mpl_df, extra_row])

        return mpl_df

    def _color(self, reason: str, order: Order, finish_price: float) -> str:
        color = "red"

        if (order.action == CandleAction.BUY and finish_price >= order.entry) or (
            order.action == CandleAction.SELL and finish_price <= order.entry
        ):
            color = "green"

        return color

    def _title(self, order: Order, reason: str) -> str:
        first = "Buy deal" if order.action == CandleAction.BUY else "Sell deal"
        second = ""

        match reason:
            case Constants.BUY_SL | Constants.SELL_SL:
                second = "ended by SL"
            case (
                Constants.BUY_TP
                | Constants.SELL_TP
                | Constants.BUY_LOSS
                | Constants.SELL_LOSS
            ):
                # _, _, second = reason.partition(" ")
                parts = reason.split(" ", 2)
                second = parts[2] if len(parts) > 2 else ""

        return f"{first} {second}"

    def _path_suffix(self, order: Order, reason: str) -> str:
        first = "buy_deal" if order.action == CandleAction.BUY else "sell_deal"
        second = ""

        match reason:
            case Constants.BUY_SL | Constants.SELL_SL:
                second = "SL"
            case Constants.BUY_TP | Constants.SELL_TP:
                second = "profit"
            case Constants.BUY_LOSS | Constants.SELL_LOSS:
                second = "loss"

        return f"{first}_{second}"

    def _finish_price(self, order: Order, candle: Candle) -> float:
        result = -1.0

        match order.action:
            case CandleAction.BUY if round(candle.low - 0.01, 2) > round(order.sl, 2):
                result = candle.close
            case CandleAction.BUY if round(candle.low - 0.01, 2) <= round(order.sl, 2):
                result = order.sl
            case CandleAction.SELL if round(candle.high, 2) < round(order.sl, 2):
                result = candle.close
            case CandleAction.SELL if round(candle.high, 2) >= round(order.sl, 2):
                result = order.sl

        return result

    def plot_simple(self, candles: list[Candle], folder_name: str, file_name: str):
        mpl_df = self._compute_df(candles=candles)

        path = os.path.join(self.parent_dir, folder_name)
        os.makedirs(path, exist_ok=True)

        date = candles[1].close_time

        fig, _ = mpf.plot(
            data=mpl_df,
            type=self.type,
            style=self.bw_gray_style,
            volume=False,
            title=str(date),
            ylabel=self.upper_name,
            ylabel_lower=self.lower_name,
            returnfig=True,
            update_width_config={"candle_width": 0.35, "volume_width": 0.35},
        )

        fig.savefig(
            os.path.join(path, file_name) + self.file_extension,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)
