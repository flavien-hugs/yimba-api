import logging
from fastapi import Request, Security, HTTPException, status
from fastapi.responses import FileResponse, Response
from fastapi.templating import Jinja2Templates

import pdfkit
from yimba_api.services import router_factory
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

TEMPLATE_DIR = str("yimba_api/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")

router = router_factory(
    prefix="/api/rapport",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get("/pdf")
async def generate_pdf(request: Request):
    context = {"request": request, "page_title": "pdf"}
    html_content = templates.TemplateResponse("pdf/pdf.html", context)

    # Generate PDF from HTML content
    pdf = pdfkit.from_string(html_content, "output.pdf", configuration=config)

    # Return the generated PDF as a response
    file_resp = FileResponse(pdf, media_type="application/pdf", filename="rapport.pdf")
    print("file response --> ", file_resp)

    response = Response(content=pdf, media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=rapport.pdf"
    return response
