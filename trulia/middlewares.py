# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class TruliaSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CaptchaMiddleware(object):
    max_retries = 5

    def process_response(request, response, spider):
        if not request.meta.get('solve_captcha', False):
            return response  # only solve requests that are marked with meta key
        catpcha = find_catpcha(response)
        if not captcha:  # it might not have captcha at all!
            return response
        solved = solve_captcha(captcha)
        if solved:
            response.meta['catpcha'] = captcha
            response.meta['solved_catpcha'] = solved
            return response
        else:
            # retry page for new captcha
            # prevent endless loop
            if request.meta.get('catpcha_retries', 0) == 5:
                logging.warning(
                    'max retries for captcha reached for {}'.format(request.url))
                raise IgnoreRequest
            request.meta['dont_filter'] = True
            request.meta['captcha_retries'] = request.meta.get(
                'captcha_retries', 0) + 1
            return request
