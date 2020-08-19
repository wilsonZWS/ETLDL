MODE_BACK_TEST = 'backtest'
MODE_PAPER_TRADE = 'papertrade'
MODE_LIVE = 'live'

VENUE_STATUS_UP = "U"
VENUE_STATUS_DOWN = "D"
TRANSACTION_ACTION_ENTER_LONG = "Enter Long"
TRANSACTION_ACTION_ENTER_SHORT = "Enter Short"
TRANSACTION_ACTION_LONG_SELL = "Long Sell"
TRANSACTION_ACTION_SHORT_BUY = "Short Buy"
TRANSACTION_ACTION_EXPAND_LONG = "Expand Long"
TRANSACTION_ACTION_EXPAND_SHORT = "Expand Short"
TRANSACTION_ACTION_LONG_REVERSE_TO_SHORT = "Long Reverse To Short"
TRANSACTION_ACTION_SHORT_REVERSE_TO_LONG = "Short Reverse To Long"
TRANSACTION_ACTION_EXIT_LONG = "Exit Long"
TRANSACTION_ACTION_EXIT_SHORT = "Exit Short"

COMMISSION_TYPE_NO = "NO"
COMMISSION_TYPE_FIX = "FIX"
COMMISSION_TYPE_PERCENTAGE = "PERCENTAGE"

MARGIN_TYPE_NO = "NO"
MARGIN_TYPE_PERCENTAGE = "PERCENTAGE"

DIR_DEFAULT_CFG = 'cfg/'

SUFFIX_CFG = '.cfg'

TAG_BARFEED = "barfeedConfig"
TAG_TICKFEED = "tickfeedConfig"

TABLE_ACCOUNT = "account"
TABLE_CONTRACT_INFO = "ContractInfo"
TABLE_PORTFOLIO = "portfolio"
TABLE_STRATEGY = "strategy"
TABLE_POSITION = "position"
TABLE_PRODUCT = "product"
TABLE_ORDER_REQUEST = "orderrequest"
TABLE_TRADE_HISTORY = "tradehistory"
TABLE_CALENDAR = "calendar"
TABLE_INSTRUMENT = "instrument"
TABLE_COMMISSION = "commission"
TABLE_INST_STATIC_AUX = "instStaticAux"
TABLE_VENUE = "venue"

POSITION_FIELDS = ['volume', 'price', 'targetTPPrice', 'targetSLPrice', 'positionRealizedPL', 'positionUnrealizedPL',
                   'positionStatus', 'assetValue', 'usedCapital', 'TP', 'SL', 'pctUnrealizedPL', 'pctRealizedPL', 'fee',
                   'ccyId', 'triggered', 'TPSLWarning']

ACCOUNT_FIELDS = ['accountId', 'totalValue', 'ccyId', 'accountStatus', 'assetValue', 'accountRealizedPL',
                  'accountUnrealizedPL', 'updateSource', 'usedCapital', 'availableCash', 'notes', 'fee', 'dividend',
                  'pctReturn', 'timestamp', 'usedMargin', 'marginLimit']

STRATEGY_FIELDS = ['strategyId', 'strategyName', 'strategyRealizedPL', 'strategyUnrealizedPL', 'strategySharpRatio',
                   'strategyMDD', 'strategyStatus', 'assetValue', 'portfolioId', 'accountId', 'updateSource',
                   'availableCash', 'usedCapital', 'notes', 'fee', 'enableTP', 'enableSL', 'timestamp', 'ccyId',
                   'TPLevel', 'SLLevel', 'usedMargin', 'marginLimit']

ORDER_FIELDS = ['orderId', 'instCode', 'orderType', 'side', 'status', 'volume', 'price', 'venueId', 'parentOrderId',
                'strategyId', 'portfolioId', 'accountId', 'timestamp', 'qualifier', 'sourceId', 'timeInForce']

TRADE_FIELDS = ['accountId', 'tradeId', 'filledVolume', 'executedPrice', 'instCode', 'side',
                'venueId', 'strategyId', 'portfolioId', 'fee', 'tradedate']

FRAME_DATA_FIELDS = ['instCode', 'date', 'frame', 'open', 'high', 'low',
                     'close', 'volume', 'amount', 'chg', 'pctChg', 'dataSrcId']

SECTOR_DATA_FIELDS = ['sectorCode', 'date', 'instCode', 'instName', 'dataSrcId']

SUSPENDED_DATA_FIELDS = ['date', 'instCode', 'status', 'susp_reason', 'timestamp']

NET_BUY_VOL_DATA_FIELDS = ['instCode', 'date', 'turn', 'free_turn_n', 'mfd_buyamt_d', 'mfd_sellamt_d',
                           'mfd_buyvol_d', 'mfd_sellvol_d', 'mfd_netbuyamt', 'mfd_netbuyvol', 'timestamp']

MFD_NET_BUY_VOL_M_DATA_FIELDS = ['instCode', 'date', 'mfd_buyvol_m', 'mfd_buyvol_open_m', 'mfd_buyvol_close_m',
                                 'mfd_inflow_m', 'mfd_inflow_open_m', 'mfd_inflow_close_m', 'timestamp']

VENUE_FIELDS = ['venueId', 'venueName', 'venueGatewayAddress', 'venueGatewayStatus', 'ccyId']

CONTRACT_INFO_FIELDS = ['contract', 'code', 'symbol', 'description', 'changeLimit', 'targetMargin', 'deliveryMonth',
                        'issueDate', 'lastTradeDate', 'lastDeliveryDate']

CALENDAR_FIELDS = ['exchId', 'tradingDate', 'dataSrcId']

WIND_FIELD_SEC_NAME = "sec_name"
WIND_FIELD_CODE = "code"
WIND_FIELD_WIND_CODE = "wind_code"
WIND_FIELD_DELIVERY_MONTH = "delivery_month"
WIND_FIELD_CHANGE_LIMIT = "change_limit"
WIND_FIELD_TARGET_MARGIN = "target_margin"
WIND_FIELD_CONTRACT_ISSUE_DATE = "contract_issue_date"
WIND_FIELD_LAST_TRADE_DATE = "last_trade_date"
WIND_FIELD_LAST_DELIVERY_MONTH = "last_delivery_month"
