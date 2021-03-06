# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection, Candidate as CanCandidate, Link, Candidate
from django.core.urlresolvers import reverse
from popit.models import Person, ApiInstance as PopitApiInstance
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from writeit.models import WriteItApiInstance, WriteItInstance
from candideitorg.models import election_finished
from writeit.models import Message as WriteItMessage
import datetime
from django.db.models import Q, Count
from django.contrib.sites.models import Site
import re
import secretballot  # import secretballot app

from django.contrib.auth.models import User


class Attachment(models.Model):
    modelName = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='attachments')
    messageId = models.IntegerField(max_length=10, null=True)
    author_id = models.IntegerField(blank=True, null=True)


class NouabookCategory(models.Model):
    name = models.CharField(max_length=255)

class NouabookItem(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True)
    text = models.TextField()
    url = models.URLField(max_length=300, blank=True, null=True)
    urlVideo = models.URLField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    candidate = models.ForeignKey(Candidate)
    category = models.ForeignKey(NouabookCategory)

class Election(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    can_election = models.OneToOneField(CanElection, null=True, blank=True)
    searchable = models.BooleanField(default=True)
    highlighted = models.BooleanField(default=False)
    popit_api_instance = models.ForeignKey(PopitApiInstance, null=True, blank=True)
    writeitinstance = models.ForeignKey(WriteItInstance, null=True, blank=True)
    extra_info_title = models.CharField(max_length=50, blank=True, null=True)
    extra_info_content = models.TextField(max_length=3000, blank=True, null=True,
                                          help_text=_("Puedes usar Markdown. <br/> ")
                                                    + markdown_allowed())
    uses_preguntales = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar preguntales?"))
    uses_ranking = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar ranking"))
    uses_face_to_face = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar frente a frente"))
    uses_soul_mate = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar 1/2 naranja"))
    uses_questionary = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar cuestionario"))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('election_view', kwargs={'slug': self.slug})

    def get_extra_info_url(self):
        return reverse('election_extra_info', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _(u'Mi Elección')
        verbose_name_plural = _(u'Mis Elecciones')


class CandidatePerson(models.Model):
    person = models.OneToOneField(Person, related_name="relation")
    candidate = models.OneToOneField(CanCandidate, related_name="relation")
    canUsername = models.OneToOneField(User, null=True, blank=True)
    reachable = models.BooleanField(default=False)
    description = models.TextField(default='', blank=True)
    portrait_photo = models.CharField(max_length=256, blank=True, null=True)
    custom_ribbon = models.CharField(max_length=18, blank=True, null=True)
    tags = TaggableManager(blank=True)
    ranking = models.IntegerField(default=0)

    def __unicode__(self):
        return u'Extra info de %(candidate)s' % {
            "candidate": self.candidate.name
        }

    def _get_twitter_(self):
        try:
            twitter = self.candidate.link_set.filter(url__contains='twitter')[0].url
            regex = re.compile(r"^https?://(www\.)?twitter\.com/(#!/)?([^/]+)(/\w+)*$")
            return regex.match(twitter).groups()[2]
        except:
            return None

    twitter = property(_get_twitter_)

    class Meta:
        verbose_name = _(u'Député: extra info activation')
        verbose_name_plural = _(u'Députés: extra info activation')


@receiver(post_save, sender=CanElection)
def automatically_create_election(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return
    can_election = instance
    if created:
        election = Election.objects.create(
            description=can_election.description,
            can_election=can_election,
            name=can_election.name,
        )
        if getattr(settings, 'USE_POPIT', True):
            popit_api_instance_url = settings.POPIT_API_URL % election.slug
        if getattr(settings, 'USE_POPIT', True):
            short_slug = hex(abs(hash(election.slug)))
            popit_api_instance_url = settings.POPIT_API_URL % short_slug
            popit_api_instance = PopitApiInstance.objects.create(
                url=popit_api_instance_url
            )
            election.popit_api_instance = popit_api_instance
            if getattr(settings, 'USE_WRITEIT', True):
                writeit_api_instance = get_current_writeit_api_instance()
                writeitinstance = WriteItInstance.objects.create(api_instance=writeit_api_instance,
                                                                 name=can_election.name)

                election.writeitinstance = writeitinstance
                election.save()


@receiver(post_save, sender=CanCandidate)
def automatically_create_popit_person(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return
    should_be_using_popit = getattr(settings, 'USE_POPIT', True)
    if not should_be_using_popit:
        return
    candidate = instance
    api_instance = candidate.election.election.popit_api_instance
    if created and api_instance:
        person = Person.objects.create(
            api_instance=api_instance,
            name=candidate.name
        )
        person.post_to_the_api()
        relation = CandidatePerson.objects.create(person=person, candidate=candidate)


@receiver(election_finished)
def automatically_push_writeit_instance(sender, instance, created, **kwargs):
    if kwargs.get('raw', False) or not created:
        return
    use_popit = getattr(settings, 'USE_POPIT', True)
    use_writeit = getattr(settings, 'USE_WRITEIT', True)
    if use_popit and use_writeit:
        election = Election.objects.get(can_election=instance)
        extra_params = {
            'popit-api': election.popit_api_instance.url
        }
        election.writeitinstance.push_to_the_api(extra_params=extra_params)


def get_current_writeit_api_instance():
    api_instance, created = WriteItApiInstance.objects.get_or_create(url=settings.WRITEIT_API_URL)
    return api_instance


class VotaInteligenteMessageManager(models.Manager):
    def get_query_set(self):
        queryset = super(VotaInteligenteMessageManager, self).get_query_set().annotate(num_answers=Count('answers'))

        return queryset.order_by('-num_answers', '-moderated', '-created')


class VotaInteligenteMessage(WriteItMessage):
    moderated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    fbshared = models.BooleanField(default=False)
    author_ville = models.CharField(max_length=35, default='')
    is_video = models.BooleanField(default=False)
    moderated_at = models.DateTimeField(editable=False, blank=True, null=True)
    first_moderation = models.BooleanField(default=False)
    pending_status = models.BooleanField(default=False)
    rejected_status = models.BooleanField(default=False)
    nouabookItem = models.ForeignKey(NouabookItem, blank=True, null=True, on_delete=models.SET_NULL)
    tags = TaggableManager(blank=True)

    objects = VotaInteligenteMessageManager()

    class Meta:
        verbose_name = _(u'Message de question')
        verbose_name_plural = _(u'Messages des questions')

    def accept_moderation(self):
        self.moderated = True
        if self.first_moderation is False:
            self.moderated_at = datetime.datetime.today()
            self.first_moderation = True
        self.save()

    def reject_moderation(self):
        self.moderated = True
        self.save()

    def __unicode__(self):
        return u'%(author_name)s preguntó "%(subject)s" en %(election)s' % {
            'author_name': self.author_name,
            'subject': self.subject,
            'election': self.writeitinstance.name
        }

    def save(self, *args, **kwargs):
        if self.first_moderation is False and self.moderated is True:
            self.moderated_at = datetime.datetime.today()
            self.first_moderation = True
            candidate = CandidatePerson.objects.get(id=self.people.first().id)

            candidate.save()
        return super(VotaInteligenteMessage, self).save(*args, **kwargs)

    @classmethod
    def push_moderated_messages_to_writeit(cls):
        query = Q(moderated=True) & Q(remote_id=None)
        messages = VotaInteligenteMessage.objects.filter(query)
        for message in messages:
            message.push_to_the_api()

    def get_absolute_url(self):
        election = self.writeitinstance.election_set.all()[0]
        path = reverse('message_detail', kwargs={'election_slug': election.slug, 'pk': self.id})
        site = Site.objects.get_current()
        return "http://%s%s" % (site.domain, path)


class VotaInteligenteAnswer(models.Model):
    message = models.ForeignKey(VotaInteligenteMessage, related_name='answers')
    content = models.TextField()
    created = models.DateTimeField(editable=False)
    person = models.ForeignKey(Person, related_name='answers')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        candidate = CandidatePerson.objects.get(id=self.person.id)

        totalQuestionsAnswred = candidate.person.answers.count()
        if totalQuestionsAnswred < 5:
            candidate.ranking = 0
        elif totalQuestionsAnswred >= 5 and totalQuestionsAnswred < 10:
            candidate.ranking = 1
        elif totalQuestionsAnswred >= 10 and totalQuestionsAnswred < 15:
            candidate.ranking = 2
        elif totalQuestionsAnswred >= 15 and totalQuestionsAnswred < 20:
            candidate.ranking = 3
        elif totalQuestionsAnswred >= 20 and totalQuestionsAnswred < 25:
            candidate.ranking = 4
        elif totalQuestionsAnswred >= 25:
            candidate.ranking = 5

        candidate.save()

        return super(VotaInteligenteAnswer, self).save(*args, **kwargs)

# enable secretballot to models using votes
secretballot.enable_voting_on(VotaInteligenteMessage)
secretballot.enable_voting_on(VotaInteligenteAnswer)
