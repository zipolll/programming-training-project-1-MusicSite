"""视图模块，实现歌曲和歌手的展示、评论和搜索功能。"""

from time import perf_counter
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from .forms import CommentForm, SearchForm
from .models import Artist, Comment, Song


class SongListView(ListView):
    """分页展示全部歌曲。"""
    model = Song
    template_name = "catalog/song_list.html"
    paginate_by = 20


class SongDetailView(DetailView):
    """展示歌曲详情，并处理评论提交。"""
    model = Song
    template_name = "catalog/song_detail.html"
    context_object_name = "song"
    pk_url_kwarg = "song_id"

    def get_queryset(self):
        """在查询歌曲时同时取得歌手和评论，避免展示时再次查询。"""
        return Song.objects.select_related("artist").prefetch_related("comments")

    def get_context_data(self, **kwargs):
        """在上下文中加入评论表单。"""
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """处理评论表单提交。"""
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.song = self.object
            comment.save()
            return redirect("catalog:song_detail", song_id=self.object.id)

        context = self.get_context_data(object=self.object)
        context["comment_form"] = form
        return self.render_to_response(context)


@require_POST # 限制下方函数只能通过 POST 方法访问，禁止 GET 方法访问。
def delete_comment(
    request: HttpRequest,
    song_id: int,
    comment_id: int,
) -> HttpResponse:
    comment = get_object_or_404(Comment, id=comment_id, song_id=song_id) # 从整个类中查找，确保评论存在且属于指定歌曲
    comment.delete()
    return redirect("catalog:song_detail", song_id=song_id)


class ArtistListView(ListView):
    """按首字母筛选并分页展示歌手。"""
    model = Artist
    template_name = "catalog/artist_list.html"
    paginate_by = 20

    def get_queryset(self):
        artists = Artist.objects.all()
        initial = self.request.GET.get("initial")
        if initial:
            artists = artists.filter(prefix=initial.upper())
        return artists

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["initial"] = self.request.GET.get("initial", "").upper()
        context["alphabet"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return context


class ArtistDetailView(DetailView):
    """展示一位歌手及其全部歌曲。"""
    model = Artist
    template_name = "catalog/artist_detail.html"
    context_object_name = "artist"
    pk_url_kwarg = "artist_id"


def search(request: HttpRequest) -> HttpResponse:
    """搜索歌曲或歌手，并记录后端查询时间。"""
    form = SearchForm(request.GET or None)
    page_obj = None
    result_count = 0
    elapsed_time = None # 记录后端查询时间，单位为秒。

    if form.is_valid():
        query = form.cleaned_data["query"] # 获取用户输入的搜索关键词
        search_type = form.cleaned_data["search_type"]
        start_time = perf_counter() # 从此处开始计时

        if search_type == "song":
            results = Song.objects.select_related("artist").filter(
                Q(title__icontains=query)
                | Q(artist__name__icontains=query)
                | Q(lyrics__icontains=query)
            ).annotate(
                search_rank=Case(
                    When(title__iexact=query, then=Value(1)),
                    When(artist__name__iexact=query, then=Value(2)),
                    When(title__istartswith=query, then=Value(3)),
                    When(title__icontains=query, then=Value(4)),
                    When(artist__name__istartswith=query, then=Value(5)),
                    When(artist__name__icontains=query, then=Value(6)),
                    default=Value(7),
                    output_field=IntegerField(), # 结果当作整数处理
                )
            ).order_by("search_rank", "title", "id")
        else:
            results = Artist.objects.filter(
                Q(name__icontains=query) | Q(introduction__icontains=query)
            ).annotate(
                search_rank=Case(
                    When(name__iexact=query, then=Value(1)),
                    When(name__istartswith=query, then=Value(2)),
                    When(name__icontains=query, then=Value(3)),
                    default=Value(4),
                    output_field=IntegerField(),
                )
            ).order_by("search_rank", "name", "id")

        paginator = Paginator(results, 20)  # 每页显示 20 条
        page_obj = paginator.get_page(request.GET.get("page"))
        result_count = paginator.count
        page_obj.object_list = list(page_obj.object_list)  # 利用 list() 强制执行查询，避免惰性查询影响计时。
        elapsed_time = perf_counter() - start_time

    return render(
        request,
        "catalog/search.html",
        {
            "form": form,
            "page_obj": page_obj,
            "result_count": result_count,
            "elapsed_time": elapsed_time,
        },
    )
