import marmot as mt

model = mt.load("vwt:add_two-v1")
print(model(13, 2))

model = mt.load("vwt:multiply_two-v1")
print(model(13, 2))

model = mt.load("vwt:add-v1")
print(model(13, 2, 1, 90, 0))

model = mt.load("vwt:multiply-v1")
print(model(13, 2, 1, 90, 0))
