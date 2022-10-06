from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from blog.forms import EmailPostForm, CommentForm
from blog.models import Post


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'list.html'


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, 'detail.html', {'post': post, 'comments': comments, 'form': form})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        # form was submitted
        if form.is_valid():
            # form field pass validation
            cd = form.cleaned_data
            # send mail
    else:
        form = EmailPostForm()
    return render(request, 'share.html', {'post': post, 'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create instance without save to database, allow modify before save
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'comment.html', {
        'post': post,
        'form': form,
        'comment': comment
    })
