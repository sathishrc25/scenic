# Copyright 2023 The Scenic Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utils for training."""

from typing import Any, Dict, Optional, Tuple

from flax.core import frozen_dict
import ml_collections
from scenic.train_lib_deprecated.train_utils import TrainState


def get_average_batch_size(config: ml_collections.ConfigDict):
  """Computes average batch size."""

  if config.get('batch_size') is not None:
    return config.batch_size

  batch_sizes_sum = 0
  n_datasets = 0

  for bs in config.batch_sizes.values():
    batch_sizes_sum += bs
    n_datasets += 1

  average_batch_size = int(batch_sizes_sum // n_datasets)

  return average_batch_size


def get_num_training_steps_multi(
    config: ml_collections.ConfigDict,
    datasets_metadata: Dict[str, Dict[str, Any]]) -> Tuple[int, Optional[int]]:
  """Calculates the total number of training step and possibly steps_per_epoch.

  The main training loop is based on number of training steps. Thus, for
  datasets
  that we want to train based on number of epochs, we need to calculate the
  total number of training steps. This function looks for `num_training_steps`
  in config, if it exists it returns that as the total step and `None` as
  `steps_per_epoch`. If num_training_steps doesn't exist, then it looks for
  `num_training_epochs` and given the size of training data calculates the total
  steps and steps_per_epoch. In this computation, we assume that
  drop_remainder=True.

  Args:
    config: Configuration of the experiment.
    datasets_metadata: Meta-data that is generated by the dataset_builder.

  Returns:
    total_steps: Total number of training steps.
    steps_per_epoch: Number of steps in every epoch.
  """
  num_total_train_examples = 0
  for ds_metadata in datasets_metadata.values():
    num_total_train_examples += ds_metadata.get('num_train_examples', 0)

  # We either use num_training_epochs or num_training_steps.
  steps_per_epoch = num_total_train_examples // get_average_batch_size(config)

  if config.get('num_training_steps'):
    assert not config.get('num_training_epochs')
    return config.num_training_steps, steps_per_epoch or None
  else:
    assert config.num_training_epochs and not config.get('num_training_steps')
    return (steps_per_epoch * config.num_training_epochs), steps_per_epoch


def pop_axes_names(
    train_state: TrainState,
    axes_name: str = 'param_axes') -> Tuple[TrainState, Optional[Any]]:
  """Removes axes_names from model_state for a train state.

  Args:
    train_state: Training state.
    axes_name: the string specifying the name in the model_state

  Returns:
    New train state without axes_names in model_state, axes_names metadata if it
    was removed (so it can be re-added).
  """
  model_state = train_state.model_state
  if axes_name in train_state.model_state:
    model_state, param_axes = frozen_dict.freeze(model_state).pop(axes_name)
    return train_state.replace(model_state=model_state), param_axes
  else:
    return train_state, None


def re_add_axis_names(train_state: TrainState,
                      param_axes: Any,
                      axes_name: str = 'param_axes') -> TrainState:
  """Adds axes_names to model_state for a train state.

  Args:
    train_state: Training state.
    param_axes: Model axes metadata to re-add.
    axes_name: the string specifying the name in the model_state

  Returns:
    New train state without axes_names in model_state, axes_names metadata if it
    was removed (so it can be re-added).
  """
  if param_axes:
    model_state = frozen_dict.unfreeze(train_state.model_state)
    model_state[axes_name] = param_axes
    return train_state.replace(model_state=frozen_dict.freeze(model_state))
  else:
    return train_state
