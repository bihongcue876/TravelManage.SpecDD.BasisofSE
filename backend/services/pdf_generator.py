# pragma: no cover
import os
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import Application, Group, Route, Participant
from services.pricing import calc_balance_deadline

_FONT_REGISTERED = False


def _register_fonts():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    _FONT_REGISTERED = True
    font_dirs = [
        "C:/Windows/Fonts",
        "/usr/share/fonts/truetype",
        "/usr/share/fonts",
    ]
    simsun = None
    simhei = None
    for d in font_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            lower = f.lower()
            if lower == "simsun.ttc" and simsun is None:
                simsun = os.path.join(d, f)
            elif lower == "simhei.ttf" and simhei is None:
                simhei = os.path.join(d, f)
            elif lower == "simhei.ttc" and simhei is None:
                simhei = os.path.join(d, f)
    if simsun:
        try:
            pdfmetrics.registerFont(TTFont("SimSun", simsun, subfontIndex=0))
        except Exception:
            pass
    if simhei:
        try:
            pdfmetrics.registerFont(TTFont("SimHei", simhei, subfontIndex=0))
        except Exception:
            pass


def _get_cn_font():
    _register_fonts()
    from reportlab.pdfbase.pdfmetrics import _fonts
    if "SimHei" in _fonts:
        return "SimHei"
    if "SimSun" in _fonts:
        return "SimSun"
    return "Helvetica"


def _build_styles(cn_font):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CNTitle",
        fontName=cn_font,
        fontSize=18,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    ))
    styles.add(ParagraphStyle(
        name="CNSubTitle",
        fontName=cn_font,
        fontSize=12,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor("#555555"),
    ))
    styles.add(ParagraphStyle(
        name="CNBody",
        fontName=cn_font,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CNBodyCenter",
        fontName=cn_font,
        fontSize=10,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CNSmall",
        fontName=cn_font,
        fontSize=8,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#888888"),
    ))
    styles.add(ParagraphStyle(
        name="CNBold",
        fontName=cn_font,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a2e"),
    ))
    styles.add(ParagraphStyle(
        name="CNFooter",
        fontName=cn_font,
        fontSize=8,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#999999"),
    ))
    styles.add(ParagraphStyle(
        name="CNImportant",
        fontName=cn_font,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=4,
        textColor=colors.HexColor("#c0392b"),
    ))
    return styles


def _fmt_amount(val) -> str:
    if val is None:
        return "0.00"
    return f"{Decimal(str(val)):,.2f}"


def _fmt_date(val) -> str:
    if isinstance(val, date):
        return val.strftime("%Y年%m月%d日")
    return str(val) if val else "-"


def _build_header(styles, title, doc_no):
    elements = []
    elements.append(Paragraph(title, styles["CNTitle"]))
    elements.append(Paragraph(f"编号：{doc_no}", styles["CNSubTitle"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a2e")))
    elements.append(Spacer(1, 8))
    return elements


def _build_confirmation(
    app: Application,
    group: Group,
    route: Route,
    participants: list,
    doc_no: str,
) -> bytes:
    cn_font = _get_cn_font()
    styles = _build_styles(cn_font)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    elements = _build_header(styles, "旅 行 确 认 书", doc_no)

    elements.append(Paragraph(
        f"尊敬的 <b>{app.name}</b> 先生/女士：", styles["CNBody"]
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "感谢您选择武汉XXX旅行社！我们已确认您的旅游申请，现将相关事项确认如下：",
        styles["CNBody"]
    ))
    elements.append(Spacer(1, 10))

    info_data = [
        ["确认编号", doc_no, "申请编号", f"AP{app.id:06d}"],
        ["路线名称", route.name, "团代码", group.code],
        ["出发日期", _fmt_date(group.departure_date), "报名截止", _fmt_date(group.deadline)],
        ["成人人数", str(app.adults), "儿童人数", str(app.children)],
        ["成人单价", f"¥{_fmt_amount(group.adult_price)}", "儿童单价", f"¥{_fmt_amount(group.child_price)}"],
        ["总费用", f"¥{_fmt_amount(app.total_price)}", "已付订金", f"¥{_fmt_amount(app.paid_deposit)}"],
        ["已付尾款", f"¥{_fmt_amount(app.paid_balance)}", "支付状态", "已全款支付" if app.paid_deposit + app.paid_balance >= app.total_price else "部分支付"],
    ]
    col_widths = [70, 145, 70, 145]
    t = Table(info_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), cn_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#1a1a2e")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    if participants:
        elements.append(Paragraph("<b>参加者名单</b>", styles["CNBold"]))
        p_header = ["序号", "姓名", "性别", "联系电话", "是否责任人"]
        p_rows = [p_header]
        for idx, p in enumerate(participants, 1):
            gender_map = {"M": "男", "F": "女", "O": "其他"}
            p_rows.append([
                str(idx),
                p.name,
                gender_map.get(p.gender, "-") if p.gender else "-",
                p.phone or "-",
                "是" if p.is_leader else "否",
            ])
        p_col_widths = [40, 100, 50, 130, 80]
        pt = Table(p_rows, colWidths=p_col_widths)
        pt.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), cn_font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ]))
        elements.append(pt)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>温馨提示</b>", styles["CNBold"]))
    tips = [
        "1. 请您于出发当日携带有效身份证件，提前30分钟到达集合地点。",
        "2. 旅途中请遵守当地法律法规，尊重当地风俗习惯，注意人身及财产安全。",
        "3. 如因不可抗力因素（如自然灾害、疫情等）导致行程变更或取消，旅行社将按相关规定处理。",
        "4. 请妥善保管本确认书，作为您参团及维权的有效凭证。",
        "5. 如需变更参加者信息或取消行程，请及时与旅行社联系，相关退费按合同约定执行。",
        "6. 旅行社已按国家旅游局规定投保旅行社责任险，建议游客自行购买旅游意外险。",
    ]
    for tip in tips:
        elements.append(Paragraph(tip, styles["CNBody"]))
    elements.append(Spacer(1, 20))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"武汉XXX旅行社 &nbsp;&nbsp;&nbsp; 签发日期：{_fmt_date(date.today())}",
        styles["CNBodyCenter"]
    ))
    elements.append(Spacer(1, 30))

    sign_data = [
        ["旅行社（盖章）", "________________", "旅客签字", "________________"],
        ["日期", _fmt_date(date.today()), "日期", _fmt_date(date.today())],
    ]
    st = Table(sign_data, colWidths=[80, 120, 80, 120])
    st.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), cn_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#1a1a2e")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "本确认书一式三份，旅行社、旅客、财务各执一份，具有同等效力。",
        styles["CNSmall"]
    ))
    elements.append(Paragraph(
        f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["CNFooter"]
    ))

    doc.build(elements)
    return buf.getvalue()


def _build_payment_notice(
    app: Application,
    group: Group,
    route: Route,
    participants: list,
    doc_no: str,
) -> bytes:
    cn_font = _get_cn_font()
    styles = _build_styles(cn_font)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    elements = _build_header(styles, "余 额 缴 款 单", doc_no)

    remaining = app.total_price - app.paid_deposit - app.paid_balance
    balance_deadline, base_deadline, fallback_deadline = calc_balance_deadline(
        group.departure_date, date.today()
    )

    elements.append(Paragraph(
        f"尊敬的 <b>{app.name}</b> 先生/女士：", styles["CNBody"]
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "根据您与武汉XXX旅行社签订的旅游申请协议，您尚有旅游费用余额未缴清，请于规定期限内完成支付。具体信息如下：",
        styles["CNBody"]
    ))
    elements.append(Spacer(1, 10))

    info_data = [
        ["缴款单编号", doc_no, "申请编号", f"AP{app.id:06d}"],
        ["路线名称", route.name, "团代码", group.code],
        ["出发日期", _fmt_date(group.departure_date), "报名截止", _fmt_date(group.deadline)],
        ["总费用", f"¥{_fmt_amount(app.total_price)}", "已付订金", f"¥{_fmt_amount(app.paid_deposit)}"],
        ["已付尾款", f"¥{_fmt_amount(app.paid_balance)}", "应付余额", f"¥{_fmt_amount(remaining)}"],
        ["支付截止日", _fmt_date(balance_deadline), "", ""],
    ]
    col_widths = [70, 145, 70, 145]
    t = Table(info_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), cn_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#1a1a2e")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("SPAN", (0, -1), (1, -1)),
        ("SPAN", (2, -1), (3, -1)),
        ("BACKGROUND", (2, -1), (3, -1), colors.HexColor("#fff3cd")),
        ("TEXTCOLOR", (2, -1), (3, -1), colors.HexColor("#c0392b")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>缴费明细</b>", styles["CNBold"]))
    detail_data = [
        ["项目", "金额（元）", "说明"],
        ["旅游总费用", f"¥{_fmt_amount(app.total_price)}", f"成人{app.adults}人×¥{_fmt_amount(group.adult_price)} + 儿童{app.children}人×¥{_fmt_amount(group.child_price)}"],
        ["已付订金", f"¥{_fmt_amount(app.paid_deposit)}", "订金已于申请时缴纳"],
        ["已付尾款", f"¥{_fmt_amount(app.paid_balance)}", "此前已缴纳的尾款金额"],
        ["应付余额", f"¥{_fmt_amount(remaining)}", "本次需缴纳的余额金额"],
    ]
    d_col_widths = [100, 100, 230]
    dt = Table(detail_data, colWidths=d_col_widths)
    dt.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), cn_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fff3cd")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#c0392b")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>缴费方式</b>", styles["CNBold"]))
    pay_methods = [
        "1. 现金支付：请前往旅行社前台缴纳（地址：武汉市XXX路XXX号）。",
        "2. 银行转账：开户行—中国工商银行武汉XXX支行，户名—武汉XXX旅行社有限公司，账号—XXXX XXXX XXXX XXXX。",
        "3. 微信/支付宝：请扫描旅行社官方收款码完成支付，备注缴款单编号。",
    ]
    for m in pay_methods:
        elements.append(Paragraph(m, styles["CNBody"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>重要提示</b>", styles["CNImportant"]))
    notices = [
        f"1. 请务必于 <b>{_fmt_date(balance_deadline)}</b> 前完成余额支付，逾期将视为自动放弃本次旅游行程。",
        "2. 支付截止日为出发前30天；若交款单发出日距截止日不足10天，截止日顺延至发出日后10天。",
        "3. 逾期未缴款者，旅行社有权取消其参团资格，已缴费用按合同约定扣除相应手续费后退还。",
        "4. 缴款后请保留缴费凭证，以便核对。如通过银行转账，请将转账回执发送至旅行社邮箱或前台确认。",
        "5. 如对本缴款单有任何疑问，请致电旅行社客服热线：027-XXXXXXXX。",
    ]
    for n in notices:
        elements.append(Paragraph(n, styles["CNBody"]))
    elements.append(Spacer(1, 20))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"武汉XXX旅行社 &nbsp;&nbsp;&nbsp; 签发日期：{_fmt_date(date.today())}",
        styles["CNBodyCenter"]
    ))
    elements.append(Spacer(1, 30))

    sign_data = [
        ["旅行社（盖章）", "________________", "旅客签字", "________________"],
        ["日期", _fmt_date(date.today()), "日期", _fmt_date(date.today())],
    ]
    st = Table(sign_data, colWidths=[80, 120, 80, 120])
    st.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), cn_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#1a1a2e")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "本缴款单一式三份，旅行社、旅客、财务各执一份，具有同等效力。",
        styles["CNSmall"]
    ))
    elements.append(Paragraph(
        f"打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["CNFooter"]
    ))

    doc.build(elements)
    return buf.getvalue()


def generate_confirmation_pdf(db, app_id: int) -> bytes:
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise ValueError("Application not found")
    group = db.query(Group).filter(Group.id == app.group_id).first()
    route = db.query(Route).filter(Route.id == group.route_id).first()
    participants = db.query(Participant).filter(Participant.application_id == app_id).all()
    today_str = date.today().strftime("%Y%m%d")
    doc_no = f"CF{today_str}{app_id:06d}"
    return _build_confirmation(app, group, route, participants, doc_no)


def generate_payment_notice_pdf(db, app_id: int) -> bytes:
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise ValueError("Application not found")
    remaining = app.total_price - app.paid_deposit - app.paid_balance
    if remaining <= 0:
        raise ValueError("余额已缴清，无需生成缴款单")
    group = db.query(Group).filter(Group.id == app.group_id).first()
    route = db.query(Route).filter(Route.id == group.route_id).first()
    participants = db.query(Participant).filter(Participant.application_id == app_id).all()
    today_str = date.today().strftime("%Y%m%d")
    doc_no = f"PO{today_str}{app_id:06d}"
    return _build_payment_notice(app, group, route, participants, doc_no)