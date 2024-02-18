import logging

from fastapi import Request, status
from fastapi.templating import Jinja2Templates

from yimba_api.services import router_factory
from yimba_api.shared import utils

logger = logging.getLogger(__name__)

TEMPLATE_DIR = str("yimba_api/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = router_factory(
    prefix="/api/rapport",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/{keyword}",
    summary="Generate rapport",
    status_code=status.HTTP_200_OK,
)
async def generate_rapport(request: Request, keyword: str):
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
