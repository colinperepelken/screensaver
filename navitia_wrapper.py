# Copyright (c) 2001-2015, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

import requests
import logging
import datetime
import _pickle as pickle

def as_time(str):
     return datetime.datetime.strptime(str, '%H%M%S').time()

class _NavitiaWrapper(object):

    def __init__(self, url, token=None, timeout=1, cache=None, query_timeout=600, pubdate_timeout=600):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.cache = self.query_timeout = self.pubdate_timeout = None
        self.set_cache(cache, query_timeout, pubdate_timeout)

    def set_cache(self, cache, query_timeout=600, pubdate_timeout=600):
        self.cache = cache
        self.query_timeout = query_timeout
        self.pubdate_timeout = pubdate_timeout

    def query(self, query, q=None, cache_timeout=None):
        logger = logging.getLogger(__name__)
        if not self.cache:
            return self._query(query, q)
        import redis
        try:
            key = 'navitiawrapper.{}.{}.{}.{}'.format(self.url, query, self.get_publication_date(), hash(frozenset(q.items())))
            rv = self.cache.get(key)
        except redis.ConnectionError:
            rv = None
            logger.exception('caching error')
        if rv is not None:
            logger.debug('cache hit')
            return pickle.loads(rv)
        logger.debug('cache miss')
        rv = self._query(query, q)
        try:
            self.cache.set(key, pickle.dumps(rv), cache_timeout or self.query_timeout)
        except redis.ConnectionError:
            logger.exception('caching error')
        return rv

    def get_publication_date(self):
        key = 'navitiawrapper.publication_date.{}'.format(self.url)
        rv = self.cache.get(key)
        if rv is not None:
            return rv
        response, status = self._query('status')
        if status == 200:
            pub_date = response['status']['publication_date']
            self.cache.set(key, pub_date, self.pubdate_timeout)
            return pub_date

        return None



    def _query(self, query, q=None):
        """
        query the API and return
        * the response as a python dict
        * the http status code
        """
        logging.getLogger(__name__).debug('query {} - Params: {}'.format(self.url + query, q))
        try:
            response = requests.get(self.url + query, auth=(self.token, None), timeout=self.timeout, params=q)
        except requests.exceptions.RequestException:
            logging.getLogger(__name__).exception('call to navitia failed')
            #currently we reraise the previous exceptions
            raise Exception('call to navitia failed, query: {}'.format(query))

        if response.status_code not in (200, 404, 400):
            raise NavitiaException('invalid call to navitia: {res} | {code}'
                                   .format(res=response.text, code=response.status_code))
        json = {}
        try:
            json = response.json()
        except Exception:
            logging.getLogger(__name__).exception('impossible to load the response as json')

        return json, response.status_code


class Navitia(object):
    def __init__(self, url, token=None, timeout=1, cache=None, query_timeout=600, pubdate_timeout=600):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.cache = cache
        self.query_timeout = query_timeout
        self.pubdate_timeout = pubdate_timeout

    def instance(self, name):
        return Instance('{url}v1/coverage/{name}/'.format(url=self.url, name=name),
                        token=self.token,
                        timeout=self.timeout,
                        cache=self.cache,
                        query_timeout=self.query_timeout,
                        pubdate_timeout=self.pubdate_timeout)


class Instance(_NavitiaWrapper):
    def _collection(self, col, uri=None, q=None):
        """
        call navitia on one collection API
        return the list of found objects (not the whole navitia response)
        """
        url = col + '/'
        if uri is not None:
            url += uri + '/'

        res, status = self.query(url, q)

        if status == 200:
            return res[col]
        return []

    def _whole_collection(self, col, uri=None, q=None):
        url = col + '/'

        if uri is not None :
            url += uri + '/'

        res, next_call = self._collection_generator_update_result(url, col, q)

        while len(res) > 0:
            yield res.pop(0)
            if len(res) == 0:
                res, next_call = self._collection_generator_update_result(next_call, col, q)

    def _collection_generator_update_result(self, next_call, collection, q):
        if next_call:
            navitia_response, status = self.query(next_call, q)
            if status == 200:
                col = collection.split('/')[-1]
                result = navitia_response[col]
                next_call_list = next((link["href"] for link in navitia_response['links'] if link['type'] == "next"), None)
                if next_call_list:
                    next_call = collection + "/" + next_call_list.split(collection)[1]
                else:
                    next_call = None
                return result, next_call
        return [], None

    def vehicle_journeys(self, uri=None, q=None):
        vehicle_journeys = self._collection('vehicle_journeys', uri, q)
        for vj in vehicle_journeys:
            for stop_time in vj.get('stop_times', []):
                if 'arrival_time' in stop_time:
                    stop_time['arrival_time'] = as_time(stop_time['arrival_time'])
                if 'departure_time' in stop_time:
                    stop_time['departure_time'] = as_time(stop_time['departure_time'])
                if 'utc_arrival_time' in stop_time:
                    stop_time['utc_arrival_time'] = as_time(stop_time['utc_arrival_time'])
                if 'utc_departure_time' in stop_time:
                    stop_time['utc_departure_time'] = as_time(stop_time['utc_departure_time'])
        return vehicle_journeys

    def stop_areas(self, uri=None, q=None):
        return self._collection('stop_areas', uri, q)

    def stop_points(self, uri=None, q=None):
        return self._collection('stop_points', uri, q)

    def networks(self, uri=None, q=None):
        return self._collection('networks', uri, q)

    def all_networks(self, uri=None, q=None):
        return self._whole_collection('networks', uri, q)

    def companies(self, uri=None, q=None):
        return self._collection('companies', uri, q)

    def physical_modes(self, uri=None, q=None):
        return self._collection('physical_modes', uri, q)


class NavitiaException(Exception):
    pass
