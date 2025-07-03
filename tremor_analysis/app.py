import csv
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

import flet as ft
import numpy as np
import yaml
from flet import ControlEvent

from tremor_analysis.analysis_methods.base import AnalysisMethodBase, AnalysisResult
from tremor_analysis.analysis_methods.coherence import CoherenceAnalysis
from tremor_analysis.analysis_methods.dummy import (
    DummyAnalysis,
    DummyAnalysisCapableTwoData,
)
from tremor_analysis.analysis_methods.power_density import PowerDensityAnalysis
from tremor_analysis.analysis_methods.spectrogram import SpectrogramAnalysis
from tremor_analysis.data_models.config_parameter import ConfigList, ConfigParameter
from tremor_analysis.ui.text_field_with_type import TextFieldWithType
from tremor_analysis.utils.yaml_file_handler import YamlFileHandler

CONFIG_FILE_PATH = Path.home() / ".tremor_analysis_config.yaml"
GENERAL_SETTINGS_KEY = "_general_"


class MainApp:
    CONFIG_DEFAULT_VALUE: ConfigList = ConfigList(
        [
            ConfigParameter(
                key="row_start", display_name="Row start", value=1, type=int
            ),
            ConfigParameter(
                key="column_start", display_name="Column start", value=1, type=int
            ),
            ConfigParameter(
                key="encoding", display_name="Encoding", value="utf-8", type=str
            ),
        ]
    )
    OUTPUT_FILE_EXTENSION = ".tremor.csv"
    ACCEPTABLE_FILE_EXTENSION = ".csv"

    def __init__(self) -> None:
        self.analysis_methods: list[AnalysisMethodBase] = [
            DummyAnalysis(),  # ここで解析手法のクラスをインスタンス化
            DummyAnalysisCapableTwoData(),
            CoherenceAnalysis(),
            PowerDensityAnalysis(),
            SpectrogramAnalysis(),
            # 他の解析手法もここに追加
        ]
        self.yaml_file_handler = YamlFileHandler(
            CONFIG_FILE_PATH,
            {
                GENERAL_SETTINGS_KEY: {
                    default.key: default.value for default in self.CONFIG_DEFAULT_VALUE
                }
            }
            | {
                method.__class__.__name__: {
                    entry.key: entry.value for entry in method.config
                }
                for method in self.analysis_methods
            },
        )
        self.apply_config_on_each_method()
        self.target_dir = ft.Text(value="Not Selected")
        self.log_content = ft.Text()
        self.file_num = 0
        self.pairs_num = 0

        self.general_setting_fields: dict[str, TextFieldWithType] = {}

    def run(self):
        results_1file: list[AnalysisResult] = []
        results_2files: list[AnalysisResult] = []
        file_list = self.scan()
        data = []

        for file_pair in file_list:
            # TODO: 正確な値に置き換え
            row_start: int = self.yaml_file_handler.content[GENERAL_SETTINGS_KEY][
                "row_start"
            ]
            column_start: int = self.yaml_file_handler.content[GENERAL_SETTINGS_KEY][
                "column_start"
            ]
            encoding: str = self.yaml_file_handler.content[GENERAL_SETTINGS_KEY][
                "encoding"
            ]
            if len(file_pair) == 1:
                data = [
                    np.loadtxt(
                        file_pair[0],
                        delimiter=",",
                        dtype=float,
                        skiprows=row_start - 1,
                        usecols=range(column_start - 1, column_start + 2),
                        encoding=encoding,
                    )
                ]
                pass
            elif len(file_pair) == 2:
                data = [
                    np.loadtxt(
                        file_pair[0],
                        delimiter=",",
                        dtype=float,
                        skiprows=row_start - 1,
                        usecols=range(column_start - 1, column_start + 2),
                        encoding=encoding,
                    ),
                    np.loadtxt(
                        file_pair[1],
                        delimiter=",",
                        dtype=float,
                        skiprows=row_start - 1,
                        usecols=range(column_start - 1, column_start + 2),
                        encoding=encoding,
                    ),
                ]
                pass
            else:
                raise NotImplementedError
            if self.target_dir:
                for method in self.analysis_methods:
                    if method.ACCEPTABLE_DATA_COUNT == 1:
                        for i, file in enumerate(file_pair):
                            result = method.run([data[i]])
                            result.filename1 = file_pair[i]
                            results_1file.append(result)
                    elif method.ACCEPTABLE_DATA_COUNT == 2 and len(file_pair) == 2:
                        # 左右の手のデータペアを受け入れる解析
                        result = method.run(data)
                        result.filename1 = file_pair[0]
                        result.filename2 = file_pair[1]
                        results_2files.append(result)
                    elif method.ACCEPTABLE_DATA_COUNT == 2 and len(file_pair) == 1:
                        pass
                    else:
                        raise NotImplementedError
        self.append_result_file(
            results_1file=results_1file,
            results_2files=results_2files,
        )

    def append_result_file(
        self,
        results_1file: list[AnalysisResult],  # ファイル名：結果
        results_2files: list[AnalysisResult],
    ) -> None:

        # ファイルごとに解析結果をまとめる
        def group_results_by_file(
            results: list[AnalysisResult],
        ) -> dict[str, list[AnalysisResult]]:
            """ファイルごとに解析結果をグループ化する"""
            grouped = {}
            for result in results:
                filename = result.filename1
                if filename not in grouped:
                    grouped[filename] = []
                grouped[filename].append(result)
            return grouped

        # ファイルごとにヘッダーを作成
        def create_header_from_grouped_results(
            grouped_results: dict[str, list[AnalysisResult]],
        ) -> list[str]:
            """グループ化された結果からヘッダーを作成"""
            header = []

            # 全てのファイルに対して全ての解析が行われる前提のもと
            # そのため，0番目のファイルに対する結果を見ればOKとした
            file_results = grouped_results[list(grouped_results.keys())[0]]
            for result in file_results:
                header += [
                    f"{result.analysis_method_class.__qualname__}_{key}"
                    for key in result.numerical_result.keys()
                ]
            return sorted(list(set(header)))

        # ファイルごとに結果行を作成
        def create_result_row(
            filename: str, file_results: list[AnalysisResult], header: list[str]
        ) -> list:
            """ファイルごとに結果行を作成"""
            result_dict = {}
            for result in file_results:
                for key, value in result.numerical_result.items():
                    header_key = f"{result.analysis_method_class.__qualname__}_{key}"
                    result_dict[header_key] = value

            # ヘッダーの順序に従って値を取得
            result_row = [result_dict.get(header_key, "") for header_key in header]
            return [filename] + result_row

        #  単一ファイルの結果出力
        output_1file = os.path.join(
            self.target_dir.value, "result_1file" + self.OUTPUT_FILE_EXTENSION
        )

        # ファイルごとに結果をグループ化
        grouped_results_1file = group_results_by_file(results_1file)

        # ヘッダー作成
        header = create_header_from_grouped_results(grouped_results_1file)

        #  出力先ファイルの存在確認,なかったらheader書き込み
        if not os.path.isfile(output_1file):
            with open(output_1file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["filename"] + header)

        # ファイルごとに結果を書き込み
        with open(output_1file, "a", newline="") as file:
            writer = csv.writer(file)
            for filename, file_results in grouped_results_1file.items():
                result_row = create_result_row(filename, file_results, header)
                writer.writerow(result_row)

        output_2files = os.path.join(
            self.target_dir.value, "result_2file" + self.OUTPUT_FILE_EXTENSION
        )

        if len(results_2files) != 0:
            # 2ファイル解析の場合は、ファイルペアごとにグループ化
            grouped_results_2files = {}
            for result in results_2files:
                file_pair = (result.filename1, result.filename2)
                if file_pair not in grouped_results_2files:
                    grouped_results_2files[file_pair] = []
                grouped_results_2files[file_pair].append(result)

            # ヘッダー作成
            header = create_header_from_grouped_results(grouped_results_2files)

            # 出力先ファイルの存在確認,なかったらheader書き込み
            if not os.path.isfile(output_2files):
                with open(output_2files, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["filename1", "filename2"] + header)

            # ファイルペアごとに結果を書き込み
            with open(output_2files, "a", newline="") as file:
                writer = csv.writer(file)
                for (
                    filename1,
                    filename2,
                ), file_results in grouped_results_2files.items():
                    result_dict = {}
                    for result in file_results:
                        for key, value in result.numerical_result.items():
                            header_key = (
                                f"{result.analysis_method_class.__qualname__}_{key}"
                            )
                            result_dict[header_key] = value

                    result_row = [
                        result_dict.get(header_key, "") for header_key in header
                    ]
                    writer.writerow([filename1, filename2] + result_row)

    def on_run_click(self, e: ControlEvent):
        """Buttonのon_clickでは, 引数にControlEventが渡されるが，run()では不要のため, この関数でwrapしている

        Args:
            e (ControlEvent): click event
        """
        self.run()

    def read_config_file(self, e: ControlEvent):
        with open(CONFIG_FILE_PATH) as file:
            self.config = yaml.safe_load(file)
        print(self.config)

    def write_config_file(self, e: ControlEvent):
        self.config["key1"] = "change"
        self.config["add_key"] = "add"
        with open(CONFIG_FILE_PATH, "w") as file:
            yaml.dump(self.config, file)
        print(self.config)

    # select folder
    def on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.target_dir.value = e.path
            self.page.update()

    def show_pick_folder(self, _: ft.ControlEvent):
        self.folder_picker.get_directory_path()

    def on_scan_click(self, _: ft.ControlEvent):
        self.scan()

    # scan directory
    def scan(self) -> list[list[str]]:
        if self.target_dir.value != "Not Selected":
            file_list = []
            self.file_num = 0
            self.pairs_num = 0

            # 最大3階層まで再帰的にディレクトリを探索
            def recursive_search(directory, depth):
                if depth > 3:
                    return
                csv_files = [
                    f
                    for f in os.listdir(directory)
                    if f.endswith(self.ACCEPTABLE_FILE_EXTENSION)
                    and not f.endswith(self.OUTPUT_FILE_EXTENSION)
                ]
                self.file_num += len(csv_files)
                if len(csv_files) == 2:
                    file_list.append(
                        tuple(os.path.join(directory, file) for file in csv_files)
                    )
                    self.pairs_num += 1

                elif len(csv_files) == 1:
                    file_list.append((os.path.join(directory, csv_files[0]),))
                else:
                    for item in os.listdir(directory):
                        path = os.path.join(directory, item)
                        if os.path.isdir(path):
                            recursive_search(path, depth + 1)

            recursive_search(self.target_dir.value, 0)

            # log_outputsの中身更新
            self.log_content.value = f"{self.file_num}files\n{self.pairs_num}pairs\nanalysis files\n{file_list}"

        else:  # Not Selected なら
            self.log_content.value = "No folder is selected"

        self.page.update()
        return file_list

    def on_open_result_click(self, _: ft.ControlEvent):
        self.open_result()

    # open result directory
    def open_result(self):
        if platform.system() == "Windows":  # Windows
            subprocess.Popen(["explorer", self.target_dir.value], shell=True)
        elif platform.system() == "Darwin":  # Mac
            subprocess.Popen(["open", self.target_dir.value])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.target_dir.value])
        return

    def on_apply_setting_click(self, _: ft.ControlEvent) -> None:
        self.apply_settings()

    # apply settings
    def apply_settings(self) -> None:
        yaml_file_content_tmp: dict[str, Any] = {}
        yaml_file_content_tmp[GENERAL_SETTINGS_KEY] = {
            key: general_config.value
            for key, general_config in self.general_setting_fields.items()
        }
        for method in self.analysis_methods:
            yaml_file_content_tmp[method.__class__.__name__] = {}
            for config, config_component in zip(
                method.config, method.configure_ui_components.values()
            ):
                config.value = config_component.value
                yaml_file_content_tmp[method.__class__.__name__][
                    config.key
                ] = config_component.value
        if yaml_file_content_tmp != self.yaml_file_handler.content:
            self.yaml_file_handler.content = yaml_file_content_tmp
            self.yaml_file_handler.export_yaml()
        self.apply_config_on_each_method()

    def build_ui(self):
        self.folder_picker = ft.FilePicker(on_result=self.on_folder_picked)
        self.page.overlay.append(self.folder_picker)
        select_folder_button = ft.Row(
            [
                ft.OutlinedButton(text="Select Folder", on_click=self.show_pick_folder),
                self.target_dir,
            ]
        )
        scan_button = ft.OutlinedButton(text="Scan", on_click=self.on_scan_click)
        run_button = ft.OutlinedButton(text="Run", on_click=self.on_run_click)
        open_result_button = ft.OutlinedButton(
            text="Open Result", on_click=self.on_open_result_click
        )
        apply_button = ft.OutlinedButton(
            text="Apply&Save Settings",
            on_click=self.on_apply_setting_click,
        )
        self.general_setting_fields = {
            config_key: TextFieldWithType(
                dtype=list(
                    filter(lambda x: x.key == config_key, self.CONFIG_DEFAULT_VALUE)
                )[0].type,
                default_value=config_value,
            )
            for config_key, config_value in self.yaml_file_handler.content[
                GENERAL_SETTINGS_KEY
            ].items()
        }

        settings = ft.Container(
            content=ft.Column(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "General Settings", size=15, weight=ft.FontWeight.BOLD
                            ),
                        ]
                        + [
                            ft.Container(
                                ft.Row(
                                    [
                                        ft.Text(general_config.display_name),
                                        self.general_setting_fields[
                                            general_config.key
                                        ].widget,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                padding=ft.padding.symmetric(horizontal=10),
                            )
                            for general_config in self.CONFIG_DEFAULT_VALUE
                        ]
                        + [method.configure_ui() for method in self.analysis_methods],
                        scroll=ft.ScrollMode.ALWAYS,
                        height=self.page.window_height * 0.6,
                    ),
                    apply_button,
                ]
            ),
            padding=15,
            width=450,
        )
        log_outputs = ft.Container(
            content=(
                ft.Column(
                    [
                        ft.Text("Log Outputs"),
                        ft.Container(
                            content=ft.Column(
                                [self.log_content],
                                height=self.page.window_height * 0.7,
                                width=400,
                                scroll=ft.ScrollMode.ALWAYS,
                            ),
                            border=ft.border.all(1, "black"),
                            padding=10,
                        ),
                    ],
                )
            ),
        )

        self.page.add(
            select_folder_button,
            ft.Row(
                [
                    ft.Container(
                        content=(
                            ft.Column(
                                [
                                    settings,
                                    scan_button,
                                    run_button,
                                    open_result_button,
                                ]
                            )
                        ),
                    ),
                    log_outputs,
                ]
            ),
        )
        return

    def apply_config_on_each_method(self):
        for method in self.analysis_methods:
            config = self.yaml_file_handler.content[method.__class__.__name__]
            method.update_config(config)

    def main(self, page: ft.Page):

        self.page = page

        # page setting
        self.page.title = "tremor_analysis"
        self.page.window_height = 750
        self.page.window_width = 1000

        self.build_ui()
        self.page.update()
        page.update()


def main():
    app = MainApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
