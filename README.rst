cleverbot.py
============

cleverbot.py is a Cleverbot API wrapper for Python made to be both
fully-featured and easy to use.

Example
-------

.. code:: py

    import cleverbot


    cb = cleverbot.Cleverbot('YOUR_API_KEY', timeout=60)

    text = input("Say to Cleverbot: ")
    try:
        reply = cb.say(text)
    except cleverbot.CleverbotError as error:
        print(error)
    else:
        print(reply)

Installing
----------

Install it from PyPI with pip:

::

    pip install cleverbot.py

Or install it from GitHub using git:

::

    git clone https://github.com/orlnub123/cleverbot.py
    cd cleverbot.py
    python setup.py install

If you don't have pip or git you can also download the source and run ``python
setup.py install`` on it.

To install Cleverbot with asynchronous support you'll have to use pip and be on
Python 3.4.2+.

::

    pip install cleverbot.py[async]

This is not required if you already have aiohttp.

**Requirements:**

- Python 3.2+ or 2.6+
- `A Cleverbot API key <http://www.cleverbot.com/api/>`_

**Dependencies:**

- Requests 1.0.0+
- aiohttp 1.0.0+ (Optional, for asynchronous support.)

Usage
-----

First import the module:

.. code:: py

    import cleverbot

--------------

Then initialize Cleverbot with your API key and optionally a cleverbot state
and or timeout:

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs='76nxdxIJ02AAA', timeout=60)

The cleverbot state is the encoded state of the conversation so far and
includes the whole conversation history up to that point.

--------------

You can now start talking to Cleverbot.

Get the reply from the input:

.. code:: py

    reply = cb.say("Hello")

Or alternatively get it later:

.. code:: py

    cb.say("Hello")
    reply = cb.output

If you want to talk to Cleverbot asynchronously use ``asay`` instead:

.. code:: py

    await cb.asay("Hello")

``asay`` only works if you're on Python 3.4.2+ and have aiohttp installed.
Experience with asyncio is recommended as you'll have to run it in an event
loop.

A big benefit of using ``asay`` is that it allows multiple requests to be sent
at once instead of waiting for the previous request to return a response which
can take significantly longer.

--------------

If something goes wrong with the request, such as an invalid API key an
``APIError`` will be raised containing the error message or, if you've defined
a timeout and you don't get a reply within the defined amount of seconds you'll
get a ``Timeout``.

As an example:

``cleverbot.errors.APIError: Missing or invalid API key or POST request, please
visit www.cleverbot.com/api``

You can get the error message and additionally the HTTP status like so:

.. code:: py

    try:
        cb.say("Hello")
    except cleverbot.APIError as error:
        print(error.error, error.status)

This is also applicable to ``Timeout`` where you can get the defined timeout
value with ``error.timeout``.

Also, all Cleverbot errors subclass ``CleverbotError`` so you can use it to
catch everything Cleverbot related.

--------------

Print out all of the data Cleverbot gained from the previous conversation:

.. code:: py

    print(cb.data)

To access them you can either use them like an attribute or directly get them
from ``cb.data``.

For example:

.. code:: py

    cb.output

    cb.data['output']

Take note of the ``cs`` key as we'll use it to save the conversation in the
next section.

To get a list of all of the keys' descriptions either take a look at the
``_query`` method's docstring in cleverbot.py or go to the JSON Reply section
in `the official Cleverbot API docs <https://www.cleverbot.com/api/howto/>`_.

--------------

Save the conversation in preparation for a reset:

.. code:: py

    cs = cb.cs

Reset Cleverbot, deleting all of the data it's gained from the previous
conversations:

.. code:: py

    cb.reset()

Note that if you try to get the cleverbot state now you'll get an error:

``AttributeError: 'Cleverbot' object has no attribute 'cs'``

Now start right where you left off by setting the cleverbot state you saved
earlier:

.. code:: py

    cb.cs = cs

Or by setting it when creating a new Cleverbot instance:

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs=cs)

--------------

If you wish to use ``cleverbot`` as a variable name you can do one of the
following:

.. code:: py

    import cleverbot as some_other_name

.. code:: py

    from cleverbot import *
