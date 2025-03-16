import tensorflow as tf
from tf_encrypted.operations.secure_random.secure_random import secure_random_module

seed = tf.constant([-27587587, -1632666452, -21862065, -153761456, 1554788191, -1805869028, -74859994, -1320420251], dtype=tf.int32)
shape=(2,)
minval=tf.constant(-128,  dtype=tf.int8)
maxval=tf.constant(127,  dtype=tf.int8)

res = secure_random_module.secure_seeded_random_uniform(
    shape,
    seed,
    minval,
    maxval,
    name=None,
)
print("res = ",res)


# import tensorflow as tf
# from tf_encrypted.operations.secure_random.secure_random import secure_random_module

# seed = tf.constant([-27587587, -1632666452, -218620675, -15376956, 1554788191, -1805869028, -74859994, -1320420251], dtype=tf.int32)
# shape=(2,)
# minval=tf.constant(-128,  dtype=tf.int32)
# maxval=tf.constant(127,  dtype=tf.int32)

# res = secure_random_module.secure_seeded_random_uniform(
#     shape,
#     seed,
#     minval,
#     maxval,
#     name=None,
# )
# print("res = ",res)
