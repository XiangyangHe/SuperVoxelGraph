
# 本算法针对GCN的node embedding结果，在高维空间上聚类（KMeans）并降维（t-SNE）分析，针对火焰燃烧的mixfrac数据
# 能分离出外焰、中焰、内焰、非燃烧区四类


from sklearn.manifold import TSNE
import sklearn.cluster as skc  # 密度聚类
from sklearn import metrics   # 评估模型
import matplotlib.pyplot as plt
import numpy as np
import pickle
# 重点是rb和r的区别，rb是打开二进制文件，r是打开文本文件

super_voxels_low_dimensional_vectors = pickle.load(open(r'I:\supergraph buffer\spheres_uchar_400_400_400_3_node_embedding.emb','rb'))

print(super_voxels_low_dimensional_vectors.shape)


import pandas as pd

if True:

    res = []
    # 迭代不同的eps值
    for eps in np.arange(0.01, 1, 0.05):
        # 迭代不同的min_samples值
        for min_samples in range(1, 100,5):
            dbscan = skc.DBSCAN(eps=eps, min_samples=min_samples)
            # 模型拟合
            dbscan.fit(super_voxels_low_dimensional_vectors)
            # 统计各参数组合下的聚类个数（-1表示异常点）
            n_clusters_ = len([i for i in set(dbscan.labels_) if i != -1])
            # 异常点的个数
            outliners = np.sum(np.where(dbscan.labels_ == -1, 1, 0))
            # 统计每个簇的样本个数
            stats = str(pd.Series([i for i in dbscan.labels_ if i != -1]).value_counts().values)
            buf_dict = {'eps': eps, 'min_samples': min_samples, 'n_clusters': n_clusters_, 'outliners': outliners,
                        'stats': stats}
            res.append(buf_dict)
            print(buf_dict)
    # 将迭代后的结果存储到数据框中
    df = pd.DataFrame(res)
    labels = dbscan.labels_

    # db = skc.DBSCAN(eps=0.8, min_samples=150).fit(super_voxels_low_dimensional_vectors) #DBSCAN聚类方法 还有参数，matric = ""距离计算方法
    # labels = db.labels_  #和X同一个维度，labels对应索引序号的值 为她所在簇的序号。若簇编号为-1，表示为噪声
    # print('每个样本的簇标号:')
    # print(labels)
    # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # 获取分簇的数目
    # print('分簇的数目: %d' % n_clusters_)
else:
    from sklearn.cluster import KMeans
    db = KMeans(n_clusters=4).fit(super_voxels_low_dimensional_vectors)
    labels = db.labels_  # 和X同一个维度，labels对应索引序号的值 为她所在簇的序号。若簇编号为-1，表示为噪声
    raito = len(labels[labels[:] == -1]) / len(labels)  # 计算噪声点个数占总数的比例
    print('每个样本的簇标号:')
    print(labels)
    print('噪声比:', format(raito, '.2%'))
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # 获取分簇的数目

    print('分簇的数目: %d' % n_clusters_)
    print("轮廓系数: %0.3f" % metrics.silhouette_score(super_voxels_low_dimensional_vectors, labels))  # 轮廓系数评价聚类的好坏


X_tsne = TSNE(n_components=2,learning_rate=100).fit_transform(super_voxels_low_dimensional_vectors)


for i in range(n_clusters_):
    print('簇 ', i, '的所有样本:')
    one_cluster = X_tsne[labels == i]
    print(one_cluster)
    plt.scatter(one_cluster[:,0],one_cluster[:,1])

plt.show()
np.save('cluster_label', labels)


