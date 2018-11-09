import os
from pymbake import aframe
from math import fabs

from django import forms
from django.db import models
from django.conf import settings

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.documents.models import Document
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

class PymbakeFinishingPage(Page):
    introduction = models.CharField(max_length=250, null=True, blank=True, help_text="Finishing description",)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Sets the finishing general appearance",
        )
    pattern = models.BooleanField(default=False, help_text="Is it a 1x1 meter pattern?",)
    color = models.CharField(max_length=250, null=True, blank=True, help_text="Accepts hex (#ffffff) or HTML color",)
    tiling_height = models.CharField(max_length=250, default="0", help_text="Tiling height from floor in cm",)
    tiling_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Sets the tiling general appearance",
        )
    tiling_pattern = models.BooleanField(default=False,  help_text="Is it a 1x1 meter pattern?",)
    tiling_color = models.CharField(max_length=250, default="white", help_text="Accepts hex (#ffffff) or HTML color",)
    skirting_height = models.CharField(max_length=250, default="0", help_text="Skirting height from floor in cm",)
    skirting_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Sets the skirting general appearance",
        )
    skirting_pattern = models.BooleanField(default=False,  help_text="Is it a 1x1 meter pattern?",)
    skirting_color = models.CharField(max_length=250, default="white", help_text="Accepts hex (#ffffff) or HTML color",)

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        MultiFieldPanel([
            ImageChooserPanel('image'),
            FieldPanel('pattern'),
            FieldPanel('color'),
        ], heading="Appearance"),
        MultiFieldPanel([
            FieldPanel('tiling_height'),
            ImageChooserPanel('tiling_image'),
            FieldPanel('tiling_pattern'),
            FieldPanel('tiling_color'),
        ], heading="Tiling"),
        MultiFieldPanel([
            FieldPanel('skirting_height'),
            ImageChooserPanel('skirting_image'),
            FieldPanel('skirting_pattern'),
            FieldPanel('skirting_color'),
        ], heading="Skirting"),
    ]

    def extract_dxf(self):

        path_to_dxf = os.path.join(settings.STATIC_ROOT, 'pymbake/samples/finishings.dxf')
        dxf_f = open(path_to_dxf, encoding = 'utf-8')
        material_gallery= ''
        collection = aframe.parse_dxf(dxf_f, material_gallery)
        dxf_f.close()

        collection = aframe.reference_openings(collection)

        for x, data in collection.items():
            if data['2'] == 'a-wall' or data['2'] == 'a-openwall':
                data['in'] = self.title
                data['out'] = self.title
                data['left'] = self.title
                data['right'] = self.title
                collection[x] = data
            elif data['2'] == 'a-door':
                data['finishing'] = self.title
                collection[x] = data
            elif data['2'] == 'a-furniture':
                data['finishing'] = self.title
                collection[x] = data
            elif data['2'] == 'a-slab':
                data['floor'] = self.title
                data['ceiling'] = self.title
                collection[x] = data

        path_to_csv = os.path.join(settings.MEDIA_ROOT, 'documents', self.slug + '.csv')
        csv_f = open(path_to_csv, 'w', encoding = 'utf-8',)
        csv_f.write('Elem,Layer,Block,Surf,Strip,Type,X,Y,Z,Rx,Ry,Rz,Width,Depth,Height,Weight, Alert \n')

        partitions = ''
        finishings = PymbakeFinishingPage.objects#how can I restrict to self?TO DO
        output = aframe.make_html(self, collection, partitions, finishings, csv_f)
        csv_f.close()

        return output

class PymbakePartitionPage(Page):
    introduction = models.CharField(max_length=250, null=True, blank=True, help_text="Partition description",)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Sets the partition general appearance",
        )
    pattern = models.BooleanField(default=False,  help_text="Is it a 1x1 meter pattern?",)
    color = models.CharField(max_length=250, null=True, blank=True, help_text="Accepts hex (#ffffff) or HTML color",)

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        MultiFieldPanel([
            ImageChooserPanel('image'),
            FieldPanel('pattern'),
            FieldPanel('color'),
        ], heading="Appearance"),
        InlinePanel('part_layers', label="Partition layers",),
    ]

    def write_html(self):
        output = ''
        i = 1
        layers = self.part_layers.all()
        if layers:
            for layer in layers:

                thickness = fabs(float(layer.thickness)/100)
                if thickness == 0:
                    thickness = 0.1
                    name = str(i) + '- ' + layer.material + ' (variable)'
                else:
                    name = str(i) + '- ' + layer.material + ' (' + str(thickness*100) + ' cm)'
                if i == 1:
                    dist = 0
                    material = f'src: #image-{self.title}; color: {self.color}'
                else:
                    dist += dist2 + thickness/2
                    material = f'color: {aframe.cad2hex(i)}'
                i += 1
                output += f'<a-box position="0 1.5 {-dist}" material="{material}" \n'
                output += f'depth="{thickness}" height="3" width="1"> \n'
                output += f'<a-entity text="anchor: left; width: 1.5; color: black; value:{name}" \n'
                output += 'position="0.55 -1.5 0 "rotation="-90 0 0"></a-entity></a-box> \n'
                dist2 = thickness/2
        return output

class PymbakePartitionPageLayers(Orderable):
    page = ParentalKey(PymbakePartitionPage, related_name='part_layers')
    material = models.CharField(max_length=250, default="brick", help_text="Material description",)
    thickness = models.CharField(max_length=250, default="0", help_text="In centimeters",)
    weight = models.CharField(max_length=250, default="0", help_text="In kilos per cubic meter",)

    panels = [
        FieldPanel('material'),
        FieldPanel('thickness'),
        FieldPanel('weight'),
    ]

class PYMbakePeopleRelationship(Orderable, models.Model):
    """
    This defines the relationship between the `People` within the `base`
    app and the PymbakePage below. This allows People to be added to a BlogPage.

    We have created a two way relationship between PymbakePage and People using
    the ParentalKey and ForeignKey
    """
    page = ParentalKey(
        'PymbakePage', related_name='pymbake_person_relationship', on_delete=models.CASCADE
    )
    people = models.ForeignKey(
        'base.People', related_name='person_pymbake_relationship', on_delete=models.CASCADE
    )
    panels = [
        SnippetChooserPanel('people')
    ]

class PymbakePage(Page):
    introduction = models.CharField(max_length=250, null=True, blank=True, help_text="Project description",)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )
    date_published = models.DateField(
        "Date article published", blank=True, null=True
        )
    equirectangular_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Landscape surrounding your project",
        )
    dxf_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="CAD file of your project",
        )
    shadows = models.BooleanField(default=False, help_text="Want to cast shadows?",)
    fly_camera = models.BooleanField(default=False, help_text="Vertical movement of camera?",)
    double_face = models.BooleanField(default=False, help_text="Planes are visible on both sides?",)

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('introduction'),
            ImageChooserPanel('image'),
            FieldPanel('date_published'),
            InlinePanel(
                'pymbake_person_relationship', label="Author(s)",
                panels=None, min_num=1),
        ], heading="Presentation"),
        MultiFieldPanel([
            DocumentChooserPanel('dxf_file'),
            ImageChooserPanel('equirectangular_image'),
            FieldPanel('shadows'),
            FieldPanel('fly_camera'),
            FieldPanel('double_face'),
        ], heading="VR settings"),
        InlinePanel('material_images', label="Material Gallery",),
    ]

    def get_partition_children(self):
        partition_children = self.get_children().type(PymbakePartitionPage).all()
        return partition_children

    def get_finishing_children(self):
        finishing_children = self.get_children().type(PymbakeFinishingPage).all()
        return finishing_children

    def extract_dxf(self):

        path_to_dxf = os.path.join(settings.MEDIA_ROOT, 'documents', self.dxf_file.filename)
        dxf_f = open(path_to_dxf, encoding = 'utf-8')
        material_gallery=self.material_images.all()
        collection = aframe.parse_dxf(dxf_f, material_gallery)
        dxf_f.close()

        collection = aframe.reference_openings(collection)
        collection = aframe.reference_animations(collection)

        path_to_csv = os.path.join(settings.MEDIA_ROOT, 'documents', self.slug + '.csv')
        csv_f = open(path_to_csv, 'w', encoding = 'utf-8',)
        csv_f.write('Elem,Layer,Block,Surf,Strip,Type,X,Y,Z,Rx,Ry,Rz,Width,Depth,Height,Weight, Alert \n')

        partitions = PymbakePartitionPage.objects.child_of(self)
        finishings = PymbakeFinishingPage.objects.child_of(self)
        output = aframe.make_html(self, collection, partitions, finishings, csv_f)
        csv_f.close()

        return output

    def get_csv_path(self):
        path_to_csv = os.path.join(settings.MEDIA_URL, 'documents', self.slug + '.csv')
        return path_to_csv

    def authors(self):
        """
        Returns the PymbakePage's related People. Again note that we are using
        the ParentalKey's related_name from the PymbakePeopleRelationship model
        to access these objects. This allows us to access the People objects
        with a loop on the template. If we tried to access the blog_person_
        relationship directly we'd print `blog.PymbakePeopleRelationship.None`
        """
        authors = [
            n.people for n in self.pymbake_person_relationship.all()
        ]

        return authors

class PymbakePageMaterialImage(Orderable):
    page = ParentalKey(PymbakePage, related_name='material_images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name = '+',
        help_text="Sets general appearance of material",
    )
    layer = models.CharField(max_length=250, default="0", help_text="Layer name in CAD file",)
    color = models.CharField(max_length=250, default="white", help_text="Accepts hex (#ffffff) or HTML color",)
    pattern = models.BooleanField(default=False, help_text="Is it a 1x1 meter pattern?",)
    invisible = models.BooleanField(default=False, help_text="Hide layer?",)

    panels = [
        FieldPanel('layer'),
        FieldPanel('invisible'),
        ImageChooserPanel('image'),
        FieldPanel('pattern'),
        FieldPanel('color'),
    ]

class PymbakeIndexPage(Page):
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
    ]

    # Speficies that only PymbakePage objects can live under this index page
    subpage_types = ['PymbakePage']

    # Defines a method to access the children of the page (e.g. PymbakePage
    # objects).
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # http://docs.wagtail.io/en/latest/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(PymbakeIndexPage, self).get_context(request)
        context['posts'] = PymbakePage.objects.descendant_of(
            self).live().order_by(
            '-first_published_at')
        return context
