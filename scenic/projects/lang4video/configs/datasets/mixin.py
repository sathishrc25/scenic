# Copyright 2024 The Scenic Authors.
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

"""Mixin config for datasets."""

import ml_collections


def get_config(run_local: str = '') -> ml_collections.ConfigDict:  # pylint: disable=unused-argument
  """Returns the experiment configuration."""
  config = ml_collections.ConfigDict()
  # Used when we need to show the name of the dataset:
  config.dataset_canonical_name = ''
  return config
