# import numpy as np
# import matplotlib.pyplot as plt
#
# fig, (ax, ax2) = plt.subplots(2, 1, sharey=True)
#
#
# ax.scatter(np.linspace(0, 10, 1000), np.random.uniform(0, 5, 1000), s=10, color='r')
# ax2.plot(np.linspace(0, 10, 1000), np.random.uniform(5, 10, 1000), color='c')
#
#
# # fig2= plt.figure(2)
# #
# # ax = fig2.add_subplot(121)
# # ax2 = fig2.add_subplot(122)kkkkkk
# #
# # ax.scatter(np.linspace(0, 10, 1000), np.random.uniform(0, 5, 1000))
# # ax2.scatter(np.linspace(0, 10, 1000), np.random.uniform(5, 10, 1000))
# plt.show()

import matplotlib.pyplot as plt
#
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot([1, 2, 3, 4], [10, 20, 25, 30], color='lightblue', linewidth=3, label='리턴')
ax.scatter([0.3, 3.8, 1.2, 2.5], [11, 25, 9, 26], color='darkgreen', marker='^', label='2')

plt.legend()

#
# fig2 = plt.figure()
#
# ax3 = fig2.add_subplot(111)
# ax3.plot([1, 2, 3, 4], [10, 20, 25, 30], color='lightblue', linewidth=3)
# ax3.scatter([0.3, 3.8, 1.2, 2.5], [11, 25, 9, 26], color='darkgreen', marker='^')
plt.show()


# plt.plot([1, 2, 3, 4], [10, 20, 25, 30], color='lightblue', linewidth=3)
# plt.scatter([0.3, 3.8, 1.2, 2.5], [11, 25, 9, 26], color='darkgreen', marker='^')
# plt.xlim(0.5, 4.5)
# plt.show()
















