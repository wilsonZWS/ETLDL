class Frequency(object):
    """Enum like class for bar frequencies. Valid values are:
    * **Frequency.TRADE**: The bar represents a single trade.
    * **Frequency.SECOND**: The bar summarizes the trading activity during 1 second.
    * **Frequency.MINUTE**: The bar summarizes the trading activity during 1 minute.
    * **Frequency.HOUR**: The bar summarizes the trading activity during 1 hour.
    * **Frequency.DAY**: The bar summarizes the trading activity during 1 day.
    * **Frequency.WEEK**: The bar summarizes the trading activity during 1 week.
    * **Frequency.MONTH**: The bar summarizes the trading activity during 1 month.
    """

    # It is important for frequency values to get bigger for bigger windows.
    TRADE = -1
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60
    WEEK = 24 * 60 * 60 * 7
    MONTH = 24 * 60 * 60 * 30

class Database(object):
    # def addBars(self, bars, frequency):
    #     for instrument in bars.getInstruments():
    #         bar = bars.getBar(instrument)
    #         self.addBar(instrument, bar, frequency)
    #
    # def addBarsFromFeed(self, feed):
    #     for dateTime, bars in feed:
    #         if bars:
    #             self.addBars(bars, feed.getFrequency())
    #
    # def addBar(self, instrument, bar, frequency):
    #     raise NotImplementedError()

    def getBars(self, instrument, frame, timezone=None, fromDateTime=None, toDateTime=None):
        raise NotImplementedError()
