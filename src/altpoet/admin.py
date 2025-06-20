from django.contrib import admin
from django.utils.safestring import mark_safe

# Register your models here.

from . import models
from .ai import ai_alts

admin.site.register(models.Project)
    

@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'item', 'created', 'img_count', 'lang')
    date_hierarchy = 'created'
    ordering = ['item']
    readonly_fields = ('project', 'created', 'item')
    search_fields = ['item__exact']
    actions = ['ai_alts']

    @admin.display(description="Project Name")
    def project_name(self, obj):
        return obj.project.name

    @admin.action(description="Get AI descriptions")
    def ai_alts(self, request, queryset):
        numdocs = 0
        alts = []
        for document in queryset:
            numdocs += 1
            alts += ai_alts(document)
        self.message_user(request, f'made {len(alts)} alt descriptions for {numdocs} documents')

    @admin.display(description="img count")
    def img_count(self, obj):
        return str(len(list(obj.imgs.all())))


@admin.register(models.Img)
class ImgAdmin(admin.ModelAdmin):
    search_fields = ['document']
    list_display = ['img_id', 'document_id', ]
    readonly_fields = ['document','image', 'alt']

    @admin.display(description="Document")
    def document_id(self, obj):
        return obj.document.item 

@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['url', 'url_display']
    search_fields = ['url']
    readonly_fields = ['url', 'x', 'y', 'filesize', 'url_display', 'hash']
    
    @admin.display(description="Image")
    def url_display(self, obj):
        return mark_safe(f"<br><img style='max-height:100px' src='{obj.url}' />")
    

@admin.register(models.Alt)
class AltAdmin(admin.ModelAdmin):
    list_display = ('text', 'img', 'source')
    readonly_fields = ['img']
    search_fields = ['text']

@admin.register(models.UserSubmission)
class UserSubAdmin(admin.ModelAdmin):
    list_display = ('source', 'document')
    search_fields = ['source', 'document']



