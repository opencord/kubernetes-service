# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

squelched_messages = {}


def debug_once(msg, *args, **kwargs):
    """ Output a given debug message only once. If we see the same messag
        again, then ignore it.
    """
    count = squelched_messages.get(msg, 0)

    if count == 0:
        # This is the first time we've seen this message.
        log.debug(msg, *args, **kwargs)
    elif count == 1:
        # We've seen a duplicate. Let the user know we're supressing.
        log.debug("[Further messages suppressed] " + msg, *args, **kwargs)

    squelched_messages[msg] = count + 1
