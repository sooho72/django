# from django.http import HttpResponse

import os
import uuid
from mysite import settings

from urllib.parse import quote
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from .models import Posts
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q 

from .form import PostCreateFrom
from .form2 import PostUpdateForm
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
# 게시글 등록
# def create_post(request):
#     return HttpResponse('게시글 등록')
def create_post(request):
    form = PostCreateFrom()

    if request.method == 'POST' :
        form = PostCreateFrom(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.password = make_password(form.cleaned_data['password'])
            post.save()

            # 파일업로드
            if request.FILES.get('uploadFile'):
                filename = uuid.uuid4().hex
                file = request.FILES.get('uploadFile')

            #파일 저장 경로
            file_path = os.path.join(settings.MEDIA_ROOT, 'posts', str(post.id), str(filename))
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            #파일저장
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            post.filename = filename
            post.original_filename = file.name
            post.save()

            messages.success(request,'게시글이 등록되었습니다.')
            return redirect("posts:read", post_id = post.id)
        else:
            messages.error(request, '게시글 등록에 실패했습니다.')

    return render(request,'posts/create.html',{'form' : form})

# 게시글 보기
# def get_post(request, post_id):
#     return HttpResponse('게시글 보기')

def get_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    return render(request,'posts/read.html', {
        'post':post,})

# 게시글 수정 
# def update_post(request, post_id):
#     return HttpResponse('게시글 수정')
def update_post(request, post_id):
    # 게시글 객체 가져오기
    post = get_object_or_404(Posts, id=post_id)
    post_password = post.password
    form = PostUpdateForm(instance=post)

    if request.method == 'POST':
        form = PostUpdateForm(request.POST)

        if form.is_valid():
            if check_password(form.cleaned_data['password'], post_password):
                post = form.save(commit=False)
                post.password = make_password(form.cleaned_data['password'])
                post.save()

                print("암호화된 비밀번호:", post.password)
                print("입력된 비밀번호:", form.cleaned_data['password'])
                print("비밀번호 일치 여부:", check_password(form.cleaned_data['password'], post.password))

                # 파일 삭제 처리
                if form.cleaned_data.get('deleteFile'):
                    if post.filename:
                        # 파일 삭제
                        file_path = os.path.join(
                            settings.MEDIA_ROOT, 'posts', str(post.id), str(post.filename)
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)

                        post.filename = None
                        post.original_filename = None
                        post.save()

                # 파일 업로드 처리
                if request.FILES.get('uploadFile'):
                    # 기존 파일 삭제
                    if post.filename:
                        file_path = os.path.join(settings.MEDIA_ROOT, 'posts', str(post.id), str(post.filename))
                        if os.path.exists(file_path):
                            os.remove(file_path)

                    # 새 파일 이름 생성
                    filename = uuid.uuid4().hex
                    file = request.FILES['uploadFile']

                    # 파일 저장 경로 생성
                    file_path = os.path.join(settings.MEDIA_ROOT, 'posts', str(post.id), str(filename))
                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # 파일 저장
                    with open(file_path, 'wb') as f:
                        for chunk in file.chunks():
                            f.write(chunk)

                    # 파일 정보 저장
                    post.filename = filename
                    post.original_filename = file.name
                    post.save()

                messages.success(request,'게시글 수정되었습니다.')
                return redirect("posts:read", post_id = post.id)
            else:
                messages.error(request, '비밀번호가 일치하지 않습니다.')
        else:
            messages.error(request, '게시글 등록에 실패했습니다.')

    return render(request,'posts/update.html',{'form' : form})


# 게시글 삭제
# def delete_post(request, post_id):
#     return HttpResponse('게시글 삭제')

def delete_post(request, post_id):
    post= get_object_or_404(Posts, id=post_id)
    
    if request.method == 'POST':
        password = request.POST.get('password')
        if check_password(password, post.password):
            print("암호화된 비밀번호:", post.password)
            print("입력된 비밀번호:", form.cleaned_data['password'])
            print("비밀번호 일치 여부:", check_password(form.cleaned_data['password'], post.password))

            # 파일삭제
            if post.filename:
                file_path = os.path.join(settings.MEDIA_ROOT,'posts', str(post.id),str(post.filename))
                if os.path.exists(file_path):
                    os.remove(file_path)

            post.delete()
            messages.success(request, '게시글이 삭제되었습니다.')
            return redirect('posts:list')
        else:
            messages.error(request, '비밀번호가 일치하지 않습니다,')
    return redirect('posts:read', post_id=post.id)


# 게시글 목록
# def get_posts(request):
#     return HttpResponse('게시글 목록')

# 게시글 목록 및 검색
def get_posts(request):
    # 기본 페이지 설정
    page = request.GET.get('page', '1')
    posts = Posts.objects.all().order_by('-created_at')  # 최신순으로 정렬

    # 검색 조건 처리
    searchType = request.GET.get('searchType')
    searchKeyword = request.GET.get('searchKeyword')

    if searchType not in [None, ''] and searchKeyword not in [None, '']:
        if searchType == 'all':
            posts = posts.filter(
                Q(title__icontains=searchKeyword) |
                Q(content__icontains=searchKeyword) |
                Q(username__icontains=searchKeyword)
            )
        elif searchType == 'title':
            posts = posts.filter(title__icontains=searchKeyword)
        elif searchType == 'content':
            posts = posts.filter(content__icontains=searchKeyword)
        elif searchType == 'username':
            posts = posts.filter(username__icontains=searchKeyword)

    # 페이지네이터 설정
    paginator = Paginator(posts, 10)  # 한 페이지에 10개의 게시글 표시
    page_obj = paginator.get_page(page)  # 현재 페이지 객체

    # 현재 페이지의 첫 번째 게시글 번호 계산
    start_index = paginator.count - (paginator.per_page * (page_obj.number - 1))

    # 순번 계산하여 게시글 리스트에 추가
    for index, post in enumerate(page_obj, start=0):
        post.index_number = start_index - index

    # 템플릿으로 데이터 전달
    return render(request, 'posts/list.html', {
        'posts': page_obj,
        'searchType': searchType,
        'searchKeyword': searchKeyword
    })

  # 첨부 파일 다운로드
def download_file(request, post_id):
    # 게시글 객체 가져오기
    post = get_object_or_404(Posts, id=post_id)
    file_path = os.path.join(settings.MEDIA_ROOT, 'posts', str(post.id), str(post.filename))

    # 파일 존재 여부 확인
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:  
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            encoded_filename = quote(post.original_filename)
            response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"  # 'Content-Dispostion' 오타 수정
            return response

    # 파일이 없을 경우 404 반환
    return HttpResponse(status=404)


