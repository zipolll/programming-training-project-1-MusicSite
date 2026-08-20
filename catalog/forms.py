"""Forms used by the catalog pages."""
#定义用户可以填写的表单。

from django import forms

from .models import Comment

# 提交歌曲评论
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "评论"}

# 输入关键词并选择搜索歌曲或歌手
class SearchForm(forms.Form):
    SEARCH_TYPES = [("song", "歌曲"), ("artist", "歌手")]

    query = forms.CharField(label="关键词", max_length=20)
    search_type = forms.ChoiceField(
        label="类型",
        choices=SEARCH_TYPES,
        widget=forms.RadioSelect,
    )

