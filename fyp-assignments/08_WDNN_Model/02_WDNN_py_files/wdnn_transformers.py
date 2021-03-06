#  Standard imports
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin 

#  ZERO PADDER
class ZeroPadder(BaseEstimator, TransformerMixin):
  """Custom transformer class for padding 1D numpy array of daily kWh values so
  that the total number of days is evenly divisible into a whole number of weeks.
  
    ATTRIBUTES
    - `days_per_consumer` is the number of kWh entries in 1D array of a single consumer
    - `days_per_week` is the number of days in a week 
    - `weeks_per_consumer` is the minimum number of whole weeks which cover `days_per_consumer`
    - `padding` is the number of `pad_value`s to add to each 1D array.
    - `pad_value` is the value with which the each 1D array in `X` will be padded
    METHODS
    - `pad_zeroes(self, row)`
      Helper function to pad the right number of zeroes to a 1D numpy array `row`. 
      `row` is a single row of the 2D numpy array `X`.
    - `fit(self, X, y=None)` 
      - initializes the attributes with the correct values according to
      the input matrix `X`.
      - returns an instance of the transformer class with the attributes initialised.
    - `transform(self, X, y=None)
      - uses numpy's apply_along_axis function to apply `pad_zeroes` to each row
      of `X`. 
      - Returns 0 padded numpy matrix of dimension (m, n + padding)`
    """  
  def __init__(self):
    """Initialise attributes with dummy values so that they can be reinitialized
    when fit to the array `X`."""
    self.days_per_consumer = 0
    self.days_per_week = 7
    self.weeks_per_consumer = 0
    self.padding = 0
    self.pad_value = 0.0

  def pad_zeroes(self, row):
    """Appends zeroes to end of each 1D numpy array of kWh values"""
    return np.pad(row, pad_width=(0, self.padding), mode='constant', constant_values=self.pad_value)

  def fit(self, X, y=None):
    """Update the attributes based on X""" 
    # Find the number of days of kWh entries for each consumer
    self.days_per_consumer = X.shape[-1]

    # Find the number of weeks in these days rounded to the nearest whole number 
    self.weeks_per_consumer = np.ceil(self.days_per_consumer / self.days_per_week).astype('uint8')

    # Number of zeros for padding = number of extra days required to turn days_per_consumer
    # into a number that is equivalent to a whole number of weeks
    self.padding = self.weeks_per_consumer * self.days_per_week - self.days_per_consumer

    # Once parameters have been fit, just return the updated instance of the transformer
    return self

  def transform(self, X, y=None):
    """Transform the data according to the specified attributes"""

    # TODO: A simpler way to do this would be to use np.append(X, np.zeros((len(X), self.padding)), axis=1)
    # This will eliminate the apply_along_axis call and nested calls to pad_zeroes
    # Pad zeroes is more complicated than required for this application
    return np.apply_along_axis(self.pad_zeroes, axis=1, arr=X)


class DailyToWeekly(BaseEstimator, TransformerMixin):
  """Custom transformer class that reshapes a 1D daily kWh data to 2D weekly data.
  For compatibility with 2D CNN layers, adding a vestigial channels axis with 
  dimensionality of 1"""

  def __init__(self):
    """Initialise a DailyToWeekly transformer with attributes for channel and 
    days per week that can be used in reshaping."""
    self.days = 0
    self.weeks = 0
    self.channels = 1 
    self.days_per_week = 7

  def daily_to_weekly(self, row):
    """Helper function to reshape (n, ) into (number_of_weeks, number_of_days_per_day, 1)
    `row` is a single consumer's vector of kWh data."""
    return row.reshape((self.weeks, self.days_per_week, self.channels))

  def fit(self, X, y=None):
    """Initialise `days` and `weeks` attributes with the right values based on `X`."""
    self.days = X.shape[-1]
    self.weeks = self.days // self.days_per_week

    # Must return instance with attributes initialised
    return self

  def transform(self, X, y=None):
    """Applies the `daily_to_weekly` transformation to each row in `X`"""
    return np.apply_along_axis(self.daily_to_weekly, axis=1, arr=X)