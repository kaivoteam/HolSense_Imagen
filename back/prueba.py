def foo(bar, baz):
  print 'hello {0}'.format(bar)

  #while(1):
  #	pass

  return 'foo' + baz

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=4)

async_result1 = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo
async_result2 = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo
async_result3 = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo
async_result4 = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo

# do some other stuff in the main process


return_val = async_result1.get()  # get the return value from your function.
print return_val

return_val = async_result4.get()  # get the return value from your function.
print return_val