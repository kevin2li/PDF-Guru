import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def encrypt_pdf(doc_path: str, user_password: str, owner_password: str = None, perm: List[str] = [], output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        full_perm_dict = {
            "打开": fitz.PDF_PERM_ACCESSIBILITY,
            "复制": fitz.PDF_PERM_COPY,
            "打印": fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ,
            "注释": fitz.PDF_PERM_ANNOTATE,
            "表单": fitz.PDF_PERM_FORM,
            "插入/删除页面": fitz.PDF_PERM_ASSEMBLE,
        }
        for v in perm:
            del full_perm_dict[v]
        perm_value = sum(full_perm_dict.values())
        encrypt_meth = fitz.PDF_ENCRYPT_AES_256 # strongest algorithm
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加密.pdf")
        doc.save(
            output_path,
            encryption=encrypt_meth, # set the encryption method
            owner_pw=owner_password, # set the owner password
            user_pw=user_password, # set the user password
            permissions=perm_value, # set permissions
            garbage=3,
            deflate=True,
            incremental=doc_path==output_path
        )
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def decrypt_pdf(doc_path: str, password: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if doc.isEncrypted:
            doc.authenticate(password)
            n = doc.page_count
            doc.select(range(n))
        else:
            utils.dump_json(cmd_output_path, {"status": "error", "message": "文件没有加密!"})
            return
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-解密.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def change_password_pdf(doc_path: str, upw: str = None, new_upw: str = None, opw: str = None, new_opw: str = None, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-修改密码.pdf")
        if upw is not None and new_upw is not None and opw is not None and new_opw is not None:
            if doc.isEncrypted:
                doc.authenticate(opw)
                perms = doc.permissions
                doc.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=new_opw, user_pw=new_upw, permissions=perms, garbage=3, deflate=True)
            else:
                utils.dump_json(cmd_output_path, {"status": "error", "message": "文件没有加密!"})
                return
        elif upw is not None and new_upw is not None:
            if doc.isEncrypted:
                doc.authenticate(upw)
                perms = doc.permissions
                doc.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=new_upw, permissions=perms, garbage=3, deflate=True)
            else:
                utils.dump_json(cmd_output_path, {"status": "error", "message": "文件没有加密!"})
                return
        elif opw is not None and new_opw is not None:
            perms = doc.permissions
            doc.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=new_opw, permissions=perms, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def recover_permission_pdf(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if doc.isEncrypted:
            utils.dump_json(cmd_output_path, {"status": "error", "message": "文件已加密，请先解密!"})
            return
        doc.select(range(doc.page_count))
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-权限恢复.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
