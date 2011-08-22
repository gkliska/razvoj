
def assertEqual(expected, given):
    if (expected != given):
        raise AssertionError('Expected "%s" but was given "%s"' % (expected, given))

def assertNotEqual(expected, given):
    if (expected == given):
        raise AssertionError('Expected something different then "%s" but it was given.' % (expected, given))