import json
import yaml

"""
pip install pyyaml==6.0.1
"""


class YamlManager:

    @staticmethod
    def yaml2data(yaml_data):
        """
            将yaml转为为data
        :param yaml_data:
        :return:
        """
        return yaml.safe_load(yaml_data)

    @staticmethod
    def data2yaml(data):
        """
            将数据转为为yaml
        :param data:
        :return:
        """
        return yaml.dump(data, default_flow_style=False)


# 示例使用
if __name__ == "__main__":
    # 示例YAML数据
    _yaml_example = """
    apiVersion: v1
    kind: Pod
    metadata:
      name: my-pod
    spec:
      containers:
      - name: my-container
        image: my-image
    """

    # 转换YAML为JSON
    _data = YamlManager.yaml2data(_yaml_example)
    print(_data)

    # 转换JSON回YAML
    _yaml_data = YamlManager.data2yaml(_data)
    print(_yaml_data)
