

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def song_list(request: HttpRequest) -> HttpResponse:
    # TODO: query Song objects and add Django pagination.
    return render(request, "catalog/song_list.html")


def song_detail(request: HttpRequest, song_id: int) -> HttpResponse:
    # TODO: load the song and implement comment creation/deletion safely.
    return render(request, "catalog/song_detail.html", {"song_id": song_id})


def delete_comment(
    request: HttpRequest,
    song_id: int,
    comment_id: int,
) -> HttpResponse:
    # TODO: accept POST only, verify that the comment belongs to this song,
    # delete it, and redirect to the same song detail page.
    raise NotImplementedError


def artist_list(request: HttpRequest) -> HttpResponse:
    # TODO: query Artist objects and add Django pagination.
    return render(request, "catalog/artist_list.html")


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    # TODO: load the artist and all related songs.
    return render(
        request,
        "catalog/artist_detail.html",
        {"artist_id": artist_id},
    )


def search(request: HttpRequest) -> HttpResponse:
    # TODO: validate SearchForm, time the backend query, and paginate results.
    return render(request, "catalog/search_results.html")
