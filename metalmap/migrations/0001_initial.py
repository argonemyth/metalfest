# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Artist'
        db.create_table(u'metalmap_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('official_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('lastfm_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('ma_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('fb_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('twitter_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('avatar_url_small', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('avatar_url_big', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='metalmap_artists', null=True, to=orm['cities_light.Country'])),
        ))
        db.send_create_signal(u'metalmap', ['Artist'])

        # Adding model 'Festival'
        db.create_table(u'metalmap_festival', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('lastfm_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, unique=True, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='festivals', null=True, to=orm['cities_light.Country'])),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
            ('computed_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('lineup', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ticket_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('lastfm_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('facebook_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'metalmap', ['Festival'])

        # Adding M2M table for field artists on 'Festival'
        m2m_table_name = db.shorten_name(u'metalmap_festival_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('festival', models.ForeignKey(orm[u'metalmap.festival'], null=False)),
            ('artist', models.ForeignKey(orm[u'metalmap.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['festival_id', 'artist_id'])

        # Adding model 'Gig'
        db.create_table(u'metalmap_gig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('lastfm_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, unique=True, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='gigs', null=True, to=orm['cities_light.Country'])),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=9, decimal_places=6, blank=True)),
            ('computed_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('lineup', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ticket_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('lastfm_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('facebook_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'metalmap', ['Gig'])

        # Adding M2M table for field artists on 'Gig'
        m2m_table_name = db.shorten_name(u'metalmap_gig_artists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gig', models.ForeignKey(orm[u'metalmap.gig'], null=False)),
            ('artist', models.ForeignKey(orm[u'metalmap.artist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gig_id', 'artist_id'])


    def backwards(self, orm):
        # Deleting model 'Artist'
        db.delete_table(u'metalmap_artist')

        # Deleting model 'Festival'
        db.delete_table(u'metalmap_festival')

        # Removing M2M table for field artists on 'Festival'
        db.delete_table(db.shorten_name(u'metalmap_festival_artists'))

        # Deleting model 'Gig'
        db.delete_table(u'metalmap_gig')

        # Removing M2M table for field artists on 'Gig'
        db.delete_table(db.shorten_name(u'metalmap_gig_artists'))


    models = {
        u'cities_light.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alternate_names': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'code2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'code3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name_ascii'"}),
            'tld': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '5', 'blank': 'True'})
        },
        u'metalmap.artist': {
            'Meta': {'object_name': 'Artist'},
            'avatar_url_big': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'avatar_url_small': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'metalmap_artists'", 'null': 'True', 'to': u"orm['cities_light.Country']"}),
            'fb_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastfm_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'ma_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'official_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'metalmap.festival': {
            'Meta': {'object_name': 'Festival'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'festivals'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['metalmap.Artist']"}),
            'computed_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'festivals'", 'null': 'True', 'to': u"orm['cities_light.Country']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'lastfm_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'lineup': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'ticket_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'metalmap.gig': {
            'Meta': {'object_name': 'Gig'},
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'gigs'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['metalmap.Artist']"}),
            'computed_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'gigs'", 'null': 'True', 'to': u"orm['cities_light.Country']"}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'lastfm_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'lineup': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '6', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'ticket_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['metalmap']