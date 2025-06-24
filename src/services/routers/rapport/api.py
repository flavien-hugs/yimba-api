import logging

from fastapi import Request, Depends, status
from fastapi.templating import Jinja2Templates

from src.services import router_factory
from src.shared import utils
from src.common.helpers.permissions import CheckAccessAllow
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)

TEMPLATE_DIR = str("src/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = router_factory(
    prefix="/rapports",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{keyword}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["report:can-generate-report"]))],
    summary="Generate report",
    status_code=status.HTTP_200_OK,
)
async def generate_report(request: Request, keyword: str):
    context = {
        "request": request,
        "page_title": keyword.upper(),
    }

    fb_graphics = await utils.fb_graphic(keyword)
    fb_statistic = await utils.get_fb_analyse(keyword)
    fb_process_text = await utils.process_text_facebook(keyword)
    fb_cloudtags_image = await utils.generate_cloud_tags_facebook(keyword)

    tk_statistic = await utils.get_titktok_analyse(keyword)
    inst_statistic = await utils.get_insta_analyse(keyword)
    yt_statistic = await utils.get_yt_analyse(keyword)

    dicts = [
        fb_process_text,
        fb_cloudtags_image,
        inst_statistic,
        tk_statistic,
        fb_graphics,
        fb_statistic,
        yt_statistic,
    ]
    for d in dicts:
        context.update(d)
    return templates.TemplateResponse("pdf/pdf.html", context)
