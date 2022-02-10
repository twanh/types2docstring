# types2docstring

> Automatically generates a docstring for type annotated functions

## Usage:

`python3 -m types2docstring file.py`

Note: this project is still very much a WIP -- so backup all important files
before using this tool!!

## Example:

_Starting point:_
```python
# should get a docstring
def f(x: int) -> int:
    return x*x

# should get a docstring
def f2(x: int, y: int) -> int:
    return x*y

# not fully annotated, so should not get a docstring
def f3(x) -> int:
    return x*x

# already has a docstring, so should not get a (new) docstring.
def f5(x: int) -> int:
    """i am a docstring"""
    return x*x


# should get a docstring
def test(
    x: int,
    y: int,
    *,
    test: str
) -> int:
    if test == 'hi':
        return x*y
    else:
        return x

if True:
    # should get a docstring, with correct indentation
    def nested(x: int) -> int:
        return x*x

```
Running `python3 -m types2docstring example.py` gives:

```python
# should get a docstring
def f(x: int) -> int:
    '''
    [function description]


    :param x: [x description]
    :type x: int


    :returns: [return description]
    :rtype: int
    '''

    return x*x

# should get a docstring
def f2(x: int, y: int) -> int:
    '''
    [function description]


    :param x: [x description]
    :type x: int
    :param y: [y description]
    :type y: int


    :returns: [return description]
    :rtype: int
    '''

    return x*y

# not fully annotated, so should not get a docstring
def f3(x) -> int:
    return x*x

# already has a docstring, so should not get a (new) docstring.
def f5(x: int) -> int:
    """i am a docstring"""
    return x*x


# should get a docstring
def test(
    x: int,
    y: int,
    *,
    test: str
) -> int:
    '''
    [function description]


    :param x: [x description]
    :type x: int
    :param y: [y description]
    :type y: int
    :param test: [test description]
    :type test: str


    :returns: [return description]
    :rtype: int
    '''

    if test == 'hi':
        return x*y
    else:
        return x

if True:
    # should get a docstring, with correct indentation
    def nested(x: int) -> int:
        '''
        [function description]


        :param x: [x description]
        :type x: int


        :returns: [return description]
        :rtype: int
        '''

        return x*x
```
