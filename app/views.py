from uuid import uuid4

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

from .models import PDF, Page


def index(request):
    pdfs = request.user.pdf_set.all()
    context = {'pdfs': pdfs}
    return render(request, 'index.html', context=context)


def upload(request):
    if request.method == 'GET':
        return render(request, 'upload.html')
    
    pdf = request.FILES['pdf']
    
    if pdf.size > (100 * 1024 * 1024):
        raise Exception('File size is over 100 MB')
    if pdf.content_type != 'application/pdf':
        raise Exception('File is not PDF')
    
    pdf_model = PDF.objects.create(name=pdf._name, user=request.user)
    pdf_name = pdf._name.replace('.', '_')
    
    reader = PdfReader(pdf.file)
    for page_number, page in enumerate(reader.pages, 1):
        writer = PdfWriter()
        writer.add_page(page)
        
        uuid4_str = uuid4().__str__()
        temp_path = settings.MEDIA_ROOT / 'temp' / uuid4_str
        writer.write(temp_path)
        filename = f'{pdf_name}_{uuid4_str}_page_{page_number}.jpg'
        
        pages = convert_from_path(temp_path,
                                  poppler_path=settings.BASE_DIR / 'poppler-23.01.0' / 'Library' / 'bin')
        for page in pages:    
            page_path = settings.MEDIA_ROOT / filename
            page.save(page_path, 'JPEG')
            Page.objects.create(path=filename,
                                page_number=page_number,
                                pdf=pdf_model
                                )
    
    import os
    os.system(f'rm -r {settings.MEDIA_ROOT}/temp/*')
    return redirect('/')


def show(request, pk):
    pdf = PDF.objects.get(pk=pk)
    pdf_page = pdf.page_set.filter(page_number=pdf.current_page)[0]
    
    if str(request.user) == 'AnonymousUser':
        owner = False
    else:
        owner = request.user.pdf_set.filter(pk=pk).exists()
    
    context = {
        'owner': owner,
        'pdf_pk': pdf_page.pdf.pk,
        'pdf_name': pdf_page.pdf.name,
        'page_number': pdf_page.page_number,
        'page_path': '/media/' + pdf_page.path,
        }
    return render(request, 'show.html', context=context)


def get_page(request, pk, page_number):
    pdf_page = PDF.objects.get(pk=pk).page_set.filter(page_number=page_number)[0]
    return HttpResponse('/media/' + pdf_page.path)


def room(request, token):
    pass
