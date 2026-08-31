"""定义用户可以填写的表单。"""

from django import forms

from .models import Comment


# 提交歌曲评论
class CommentForm(forms.ModelForm):  # 表单内容需要保存到数据库，使用 ModelForm
    class Meta:
        model = Comment
        fields = ["body"]  # 规定表单只显示和接收 body 字段
        labels = {"body": "撰写评论"}  # 把 body 字段在网页中显示的标签改成“评论”。
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}  # 评论框默认显示 5 行


# 输入关键词并选择搜索歌曲或歌手
class SearchForm(forms.Form):
    SEARCH_TYPES = [("song", "歌曲"), ("artist", "歌手")]
    query = forms.CharField(label="关键词", max_length=20)
    search_type = forms.ChoiceField(
        label="类型",
        choices=SEARCH_TYPES,
        widget=forms.RadioSelect,  # 展示搜索类型时使用单选按钮
    )
