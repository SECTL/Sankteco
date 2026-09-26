"""
添加与保存名单的逻辑文件,
包含Sankteco风格名单文件的创建接口、导入及导出名单文件的接口,
引用时可作 AIENamelist / add_import_export_namelist
"""

from pathlib import Path

import tablib, qrcode
from pyzbar.pyzbar import decode
from PIL import Image

from app_const_var import LogicFilesString, AssetsPathTXT


class AIENamelist:
    """添加与保存名单的逻辑文件类,
    包含Sankteco风格名单文件的创建接口、导入及导出名单文件的接口,
    引用时可作 AIENamelist / add_import_export_namelist"""

    @staticmethod
    def add_namelist(namelist_id: str):
        """添加新名单"""

        # 创建一个空的 Dataset,并指定表头(headers)
        namelist_data = tablib.Dataset(headers=LogicFilesString.AIENAMELIST_HEADER)

        # 用 .append() 添加初始行(数据需与表头顺序对应)
        namelist_data.append([True, 1, "张三", "男", 1, ""])

        # 导出为 JSON 格式
        with open(
            f"{AssetsPathTXT.APP_NAMELISTS_FOLDER}{namelist_id}.json",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(namelist_data.export("json"))

        return f"{namelist_id}.json", namelist_data

    @staticmethod
    def import_namelist(namelist_path: str):
        """导入名单,成功返回 (Dataset, saved_path),失败返回 (None, None)"""

        path = Path(namelist_path)
        if not path.is_file() or path.stat().st_size == 0:
            return (None, None)
        ext = path.suffix.lower()

        # 判断后缀
        try:
            if ext == ".txt":
                with open(path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                dataset = AIENamelist.convert_namelist_txt(lines)
            elif ext in [".json", ".csv", ".yaml"]:
                with open(path, "r", encoding="utf-8") as f:
                    raw = tablib.Dataset().load(f, format=ext[1:])
                dataset = AIENamelist.convert_namelist_not_txt(raw)
            elif ext in [".xlsx", ".xls", ".ods"]:
                with open(path, "rb") as f:
                    raw = tablib.Dataset().load(f, format=ext[1:])
                dataset = AIENamelist.convert_namelist_not_txt(raw)
            elif ext == ".png":
                img = Image.open(path)
                # 解码
                decoded_objs = decode(img)
                if decoded_objs:
                    # 提取第一个二维码的数据(bytes)
                    data_bytes = decoded_objs[0].data
                    # 转为字符串
                    str_decoded = data_bytes.decode("utf-8")
                    # 判断是否为列表
                    try:
                        list(str_decoded)
                        raw = tablib.Dataset().load(str_decoded, format="json")
                        dataset = AIENamelist.convert_namelist_not_txt(raw)
                    except TypeError:
                        print("无效的二维码")
                else:
                    print("未识别到二维码")
            else:
                return (None, None)
        except Exception as e:
            print(f"导入失败: {e}")
            return (None, None)

        # 检查是否成功转换
        if dataset is None or len(dataset) == 0:
            return (None, None)

        # 保存为 Sankteco JSON
        saved_name = f"{path.stem}.json"
        saved_path = Path(AssetsPathTXT.APP_NAMELISTS_FOLDER) / saved_name
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(dataset.export("json"))

        return (dataset, str(saved_path))

    @staticmethod
    def export_namelist(namelist: tablib.Dataset, namelist_path: str):
        """导出名单到不同格式"""

        path = Path(namelist_path)
        ext = path.suffix.lower()

        # 判断后缀
        try:
            if ext == ".txt":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(str(val) for val in namelist[LogicFilesString.AIENAMELIST_HEADER_NAME])  # type: ignore
            elif ext in [".json", ".yaml", ".csv"]:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(namelist.export(ext[1:]))
            elif ext in [".xlsx", ".xls", ".ods"]:
                with open(path, "wb", encoding="utf-8") as f:
                    f.write(namelist.export(ext[1:]))
            elif ext == ".png":
                qr = qrcode.QRCode(
                    version=10,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,  # type: ignore
                    box_size=10,
                    border=4,
                )
                qr.add_data(namelist.export("json"))
                qr.make()
                qr.make_image(fill_color="black", back_color="white").save(path)  # type: ignore
        except Exception as e:
            print(f"导出失败: {e}")

    @staticmethod
    def convert_namelist_txt(namelist_data: list):
        """转换 .txt 名单为 Sankteco 格式"""

        no = 0

        # 按行转换为 Sankteco 格式
        namelist_sankteco_data = tablib.Dataset(
            headers=LogicFilesString.AIENAMELIST_HEADER
        )
        for i in namelist_data:
            no += 1
            namelist_sankteco_data.append([True, no, i, "", "", ""])

        return namelist_sankteco_data

    @staticmethod
    def convert_namelist_not_txt(namelist_data: tablib.Dataset):
        """转换非 .txt 名单为 Sankteco 格式,若无法识别则返回 None"""

        # 没有表头 -> 无法识别,直接拒绝
        if namelist_data.headers is None:
            return None

        headers = namelist_data.headers

        # 完全匹配 Sankteco 格式 -> 直接使用
        if headers == LogicFilesString.AIENAMELIST_HEADER:
            return namelist_data

        # 尝试根据已知列名进行转换(仅当包含编号或姓名列)
        no_idx = (
            headers.index(LogicFilesString.AIENAMELIST_HEADER_NO)
            if LogicFilesString.AIENAMELIST_HEADER_NO in headers
            else None
        )
        name_idx = (
            headers.index(LogicFilesString.AIENAMELIST_HEADER_NAME)
            if LogicFilesString.AIENAMELIST_HEADER_NAME in headers
            else None
        )

        # 如果既没有编号也没有姓名列,则无法转换
        if no_idx is None and name_idx is None:
            return None

        new_dataset = tablib.Dataset(headers=LogicFilesString.AIENAMELIST_HEADER)
        for idx, row in enumerate(namelist_data):  # type: ignore
            no = row[no_idx] if no_idx is not None else idx + 1
            name = row[name_idx] if name_idx is not None else ""
            new_dataset.append([True, no, name, "", "", ""])
        return new_dataset

    @staticmethod
    def json_to_dataset(namelist: str):
        """导出前转换名单为 dataset"""

        # 预处理为绝对路径
        namelist_path = Path.cwd() / "namelists" / namelist
        path = Path(namelist_path)

        with open(path, "r", encoding="utf-8") as f:
            dataset = tablib.Dataset().load(f, format="json")

        return dataset
