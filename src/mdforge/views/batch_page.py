from __future__ import annotations



from pathlib import Path



from PySide6.QtWidgets import (

    QFileDialog,

    QHBoxLayout,

    QLabel,

    QListWidget,

    QProgressBar,

    QPushButton,

    QSizePolicy,

    QVBoxLayout,

    QWidget,

)



from mdforge.core.batch_paths import NESTED_FLAT_MD_DIR_NAME, default_batch_output_dir

from mdforge.core.file_collector import BatchMode

from mdforge.views.batch_mode_selector import BatchModeSelector, MODE_META

from mdforge.views.components import LogPanel, PageHeader, SectionFrame

from mdforge.views.layout_utils import tune_button

from mdforge.views.widgets import PathPicker





class BatchPage(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:

        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root = QVBoxLayout(self)

        root.setSpacing(18)

        root.setContentsMargins(0, 0, 0, 0)



        root.addWidget(

            PageHeader(

                "批量转换",

                "选择来源方式后浏览文件或文件夹；输出目录可在下方修改。",

            )

        )

        self.parser_badge = QLabel()

        self.parser_badge.setObjectName("activeParserBadge")

        root.addWidget(self.parser_badge)



        source_section = SectionFrame("来源方式")

        self.mode_selector = BatchModeSelector()

        source_section.add_widget(self.mode_selector)

        self.mode_hint = QLabel()

        self.mode_hint.setObjectName("modeHint")

        self.mode_hint.setWordWrap(True)

        source_section.add_widget(self.mode_hint)

        root.addWidget(source_section)

        pick_section = SectionFrame("选择来源")

        pick_row = QHBoxLayout()

        self.pick_btn = QPushButton("浏览…")

        self.pick_btn.setObjectName("secondaryBtn")

        tune_button(self.pick_btn, fixed_width=88)

        self.clear_btn = QPushButton("清空")

        self.clear_btn.setObjectName("ghostBtn")

        tune_button(self.clear_btn, fixed_width=72)

        pick_row.addWidget(self.pick_btn, 0)

        pick_row.addWidget(self.clear_btn, 0)

        pick_row.addStretch(1)

        pick_wrap = QWidget()

        pick_wrap.setLayout(pick_row)

        pick_section.add_widget(pick_wrap)



        self.source_label = QLabel("尚未选择")

        self.source_label.setObjectName("hintLabel")

        pick_section.add_widget(self.source_label)

        self.file_list = QListWidget()

        self.file_list.setObjectName("fileList")

        self.file_list.setMinimumHeight(80)

        self.file_list.setMaximumHeight(140)

        pick_section.add_widget(self.file_list)

        root.addWidget(pick_section)

        self._update_mode_hint(BatchMode.FILES)

        out_section = SectionFrame("输出")

        self.output_picker = PathPicker("输出目录", is_directory=True)

        self.output_hint = QLabel("选择文件夹后，默认输出到同级目录「文件夹名-md」")

        self.output_hint.setObjectName("hintLabel")

        self.output_hint.setWordWrap(True)

        out_section.add_widget(self.output_picker)

        out_section.add_widget(self.output_hint)

        root.addWidget(out_section)



        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.convert_btn = QPushButton("开始批量转换")
        self.convert_btn.setObjectName("primaryBtn")
        tune_button(self.convert_btn)
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelBtn")
        tune_button(self.cancel_btn, fixed_width=88)
        self.cancel_btn.setEnabled(False)
        action_row.addWidget(self.convert_btn, 1)
        action_row.addWidget(self.cancel_btn, 0)
        action_wrap = QWidget()
        action_wrap.setLayout(action_row)
        root.addWidget(action_wrap)



        self.progress = QProgressBar()

        self.progress.setObjectName("mainProgress")

        self.progress.setRange(0, 100)

        self.progress.setValue(0)

        self.progress.setTextVisible(True)

        self.progress.hide()

        root.addWidget(self.progress)



        log_section = SectionFrame("运行日志")

        self.log = LogPanel("批量转换日志…")

        log_section.add_widget(self.log)

        root.addWidget(log_section, 1)



        self._folder: str | None = None

        self._files: list[str] = []

        self.mode_selector.mode_changed.connect(self._on_mode_changed)

        self.pick_btn.clicked.connect(self._pick_source)

        self.clear_btn.clicked.connect(self._clear_sources)



    def selected_mode(self) -> BatchMode:

        return self.mode_selector.selected_mode()



    def file_paths(self) -> list[str]:

        return list(self._files)



    def folder_path(self) -> str | None:

        return self._folder



    def set_active_parser(self, label: str) -> None:

        self.parser_badge.setText(f"  当前解析器 · {label}  ")



    def append_log(self, text: str) -> None:

        self.log.append_line(text)



    def set_busy(self, busy: bool) -> None:

        self.convert_btn.setEnabled(not busy)

        self.cancel_btn.setEnabled(busy)

        self.pick_btn.setEnabled(not busy)

        self.clear_btn.setEnabled(not busy)

        self.mode_selector.setEnabled(not busy)

        self.output_picker.set_busy(busy)

        if busy:

            self.progress.show()

        else:

            self.progress.hide()



    def set_progress(self, value: int) -> None:

        self.progress.setValue(max(0, min(100, value)))



    def _update_mode_hint(self, mode: BatchMode) -> None:

        _, _, desc = MODE_META[mode]

        extra = ""

        if mode == BatchMode.NESTED_FOLDERS:

            extra = (
                f" 完成后会在结果目录下生成「{NESTED_FLAT_MD_DIR_NAME}/」，"
                "仅含汇总的 .md（文件名与 PDF 一致）。"
            )

        self.mode_hint.setText(desc + extra)

        if mode == BatchMode.FILES:

            self.pick_btn.setText("选择 PDF…")

        else:

            self.pick_btn.setText("选择文件夹…")



    def _apply_default_output(self) -> None:

        mode = self.selected_mode()

        folder = Path(self._folder) if self._folder else None

        files = [Path(p) for p in self._files]

        suggested = default_batch_output_dir(mode, folder_path=folder, file_paths=files or None)

        if suggested:

            self.output_picker.set_path(str(suggested))

            hint = f"默认输出：{suggested}（开始转换时若不存在会自动创建）"

            if mode == BatchMode.NESTED_FOLDERS:

                hint += f"；另含 {NESTED_FLAT_MD_DIR_NAME}/ 纯 Markdown 汇总。"

            self.output_hint.setText(hint)



    def _on_mode_changed(self, mode: BatchMode) -> None:

        self._update_mode_hint(mode)

        self._clear_sources()



    def _clear_sources(self) -> None:

        self._files.clear()

        self._folder = None

        self.file_list.clear()

        self.source_label.setText("尚未选择")

        self.output_picker.set_path("")

        self.output_hint.setText("选择来源后，将自动建议输出目录（同级「文件夹名-md」）")



    def _pick_source(self) -> None:

        mode = self.selected_mode()

        start = self.output_picker.path() or ""

        if mode == BatchMode.FILES:

            paths, _ = QFileDialog.getOpenFileNames(

                self, "选择 PDF 文件", start, "PDF 文件 (*.pdf)"

            )

            if paths:

                self._files = paths

                self._folder = None

                self.file_list.clear()

                self.file_list.addItems(paths)

                self.source_label.setText(f"已选 {len(paths)} 个 PDF")

                self._apply_default_output()

        else:

            folder = QFileDialog.getExistingDirectory(self, "选择文件夹", start)

            if folder:

                self._folder = folder

                self._files.clear()

                self.file_list.clear()

                self.file_list.addItem(folder)

                label = "文件夹" if mode == BatchMode.FLAT_FOLDER else "父文件夹"

                self.source_label.setText(f"{label}：{folder}")

                self._apply_default_output()


