from flask import Flask
import numpy as np
import pandas as pd
app = Flask(__name__)
@app.route("/")
def hello():
  #df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
  for i in range(1):
    try:
      df = pd.read_csv('/mnt/data/metfidas/2015-SMP1-086.csv')
      if i > 0:
        a = pd.concat([a,df["RH"]])
      else:
        a = df["RH"]
    except Exception,e:
      return str(e)
  return a.to_frame().to_html()
#  return df.to_html()
#  a=pd.Series([1,2,3])
#  b=pd.concat([a]*4, axis=1)
#  return df.to_html()
  #return "Flask"
if __name__ == "__main__":
  app.run()
