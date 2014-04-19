from selenium import webdriver
import unittest

class HomePageTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_see_homepage(self):
        # Alice want to find checking out all the metal festivals on a nice interative
        # map.
        self.browser.get('http://localhost:8000')

        # She notices the page title and header mention 'MetalFest'
        self.assertIn('MetalFest', self.browser.title)
        self.fail('Finish the test!')

    # She notices all the metal festivals happening around the globle in
    # 2014 (77 total)

    # She notices that all upcoming ones are marked in color and past ones are
    # marked in grey

    # She wants to check all the festivals happending in July and Auguest,
    # so she set the Jul 1st and Aug 31st in the date filter box, and now she
    # saw only the festivals that are happening in July and Auguest.

    # She wants to continue filter out all the festivals that are outside of
    # the Europe, so she selected 'Europe' in the continent filter box and
    # now only the festivals in europe remains.


if __name__ == '__main__':
    unittest.main()