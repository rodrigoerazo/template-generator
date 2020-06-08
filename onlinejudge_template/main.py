import argparse
import sys
from logging import DEBUG, INFO, basicConfig, getLogger
from typing import *

import onlinejudge_template.analyzer.combined
import onlinejudge_template.generator
import onlinejudge_template.network

import onlinejudge.dispatch
import onlinejudge.utils

logger = getLogger(__name__)


def main(args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-t', '--template', default='main.cpp')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--cookie', default=onlinejudge.utils.default_cookie_path)
    parsed = parser.parse_args(args=args)

    if parsed.verbose:
        basicConfig(level=DEBUG)
    else:
        basicConfig(level=INFO)

    # download
    url = parsed.url
    problem = onlinejudge.dispatch.problem_from_url(url)
    if problem is not None:
        url = problem.get_url()  # normalize url
    logger.debug('url: %s', url)
    with onlinejudge.utils.with_cookiejar(onlinejudge.utils.get_default_session(), path=parsed.cookie) as session:
        html = onlinejudge_template.network.download_html(url, session=session)
        sample_cases = onlinejudge_template.network.download_sample_cases(url, session=session)
    logger.debug('sample cases: %s', sample_cases)

    # analyze
    resources = onlinejudge_template.analyzer.combined.prepare_from_html(html, url=url, sample_cases=sample_cases)
    logger.debug('analyzer resources: %s', resources._replace(html=b'...skipped...'))
    analyzed = onlinejudge_template.analyzer.combined.run(resources)
    logger.debug('analyzed result: %s', analyzed._replace(resources=analyzed.resources._replace(html=b'...skipped...')))

    # generate
    code = onlinejudge_template.generator.run(analyzed, template_file=parsed.template)
    sys.stdout.buffer.write(code)


if __name__ == '__main__':
    main()
