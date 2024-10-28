import React, { useEffect, useState } from 'react';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import {
  Button,
  Col,
  // Divider,
  // Empty,
  Form,
  Input,
  Modal,
  Popconfirm,
  Row,
} from 'antd';
import { SceneModalInfoWrapper } from './style';

type TagInfo = {
  [key: string]: any;
};

interface TagData extends TagInfo {
  label: string;
  value: string;
}

interface TagActionInfoProps {
  isShow: boolean;
  info: TagData[];
}

const jsonToData = () => {
  try {
    console.log(
      'tag数据',
      JSON.parse(localStorage.getItem('tagsModalData') || '[]'),
    );
    return JSON.parse(localStorage.getItem('tagsModalData') || '[]');
  } catch (err) {
    console.warn(err);
    return [];
  }
};

const SceneModalInfo = () => {
  const [tagsModalData, setTagsModalData] = useState<TagData[]>([]);
  const [isTagsModalShow, setIsTagsModalShow] = useState<boolean>(false);
  const [isAddTagsShow, setIsAddTagsShow] = useState<TagActionInfoProps>({
    isShow: false,
    info: [],
  });

  const [tagForm] = Form.useForm();

  useEffect(() => {
    setTagsModalData(jsonToData());
  }, [JSON.stringify(localStorage.getItem('tagsModalData') || '[]')]);

  return (
    <SceneModalInfoWrapper>
      {/* 本期暂无标签 */}
      {/* <Form.Item
        label={
          <Space>
            <span>标签</span>
            <Tooltip title="可用于视图的打标">
              <QuestionCircleOutlined style={{ cursor: 'pointer' }} />
            </Tooltip>
          </Space>
        }
        name="description"
      >
        <Select
          mode="multiple"
          placeholder="请选择标签"
          style={{ width: '100%' }}
          options={tagsModalData}
          notFoundContent={
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="您还没有自定义标签"
            />
          }
          dropdownRender={(menu) => (
            <>
              {menu}
              <Divider
                style={{
                  margin: '8px 0',
                }}
              />
              <Button
                type="link"
                icon={
                  <img src="https://mdn.alipayobjects.com/huamei_5qayww/afts/img/A*K39ITJeCQjIAAAAAAAAAAAAADprcAQ/original" />
                }
                onClick={() => setIsTagsModalShow(true)}
              >
                管理标签
              </Button>
            </>
          )}
        />
      </Form.Item> */}
      {isTagsModalShow && (
        <Modal
          open={isTagsModalShow}
          title="管理标签"
          onClose={() => setIsTagsModalShow(false)}
          onCancel={() => setIsTagsModalShow(false)}
          okText="保存"
          bodyStyle={{ minHeight: '680px', overflow: 'auto' }}
          getContainer={false}
          className="sceneModal"
        >
          <Row>
            <Col span={24}>
              <Button
                block
                icon={<PlusOutlined />}
                onClick={() => {
                  tagForm.resetFields();
                  setIsAddTagsShow({
                    isShow: true,
                    info: [],
                  });
                }}
                style={{ background: 'rgb(27 98 255 / 10%)', color: '#1b62ff' }}
              >
                自定义标签
              </Button>
            </Col>
          </Row>
          <Row style={{ marginTop: '12px' }}>
            {tagsModalData?.map((item: { label: string; value: string }) => {
              return (
                <Col span={24} key={item.value}>
                  <div className="tagItem">
                    <span>{item.label}</span>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div
                        className="tagIcon"
                        style={{ cursor: 'not-allowed' }}
                      >
                        <EditOutlined />
                      </div>
                      <Popconfirm
                        title=""
                        description="该标签被多个节点使用，你确定要删除吗?"
                        onConfirm={() => {
                          const newData = jsonToData()?.filter(
                            (it: { label: string; value: string }) =>
                              it.value !== item.value,
                          );
                          localStorage.setItem(
                            'tagsModalData',
                            JSON.stringify(newData),
                          );
                          setTagsModalData(newData);
                        }}
                        okText="确定"
                        cancelText="取消"
                      >
                        <div className="tagIcon">
                          <DeleteOutlined />
                        </div>
                      </Popconfirm>
                    </div>
                  </div>
                </Col>
              );
            })}
          </Row>
        </Modal>
      )}
      {isAddTagsShow && (
        <Modal
          open={isAddTagsShow.isShow}
          title="自定义标签"
          onClose={() => {
            setIsAddTagsShow({
              isShow: false,
              info: [],
            });
          }}
          onCancel={() => {
            setIsAddTagsShow({
              isShow: false,
              info: [],
            });
          }}
          onOk={() => {
            const formValue = tagForm.getFieldValue('tagNames');
            localStorage.setItem(
              'tagsModalData',
              JSON.stringify([
                ...jsonToData(),
                { label: formValue, value: formValue },
              ]),
            );
            setIsAddTagsShow({
              isShow: false,
              info: [],
            });
          }}
          okText="保存"
          style={{ top: '30%' }}
          getContainer={false}
        >
          <Row style={{ padding: '24px 0' }}>
            <Col span={24}>
              <Form form={tagForm}>
                <Form.Item label="标签" name="tagNames">
                  <Input placeholder="请输入标签名称，可用英文逗号分隔批量创建" />
                </Form.Item>
              </Form>
            </Col>
          </Row>
        </Modal>
      )}
    </SceneModalInfoWrapper>
  );
};

export default SceneModalInfo;
