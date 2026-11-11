import sys, os
sys.path.insert(0, os.path.abspath("."))
import auto_factory_batch

# Check topics before
rem = auto_factory_batch.get_remaining_topics()
print("Remaining topics count:", len(rem))
print("First topic:", auto_factory_batch.peek_first_topic())

# Check done topics before
done = auto_factory_batch.get_done_topics()
print("Done topics count:", len(done))

# Mark first topic done
first_topic = auto_factory_batch.peek_first_topic()
auto_factory_batch.mark_topic_done(first_topic)

# Check topics after
rem_after = auto_factory_batch.get_remaining_topics()
print("Remaining topics count after:", len(rem_after))
print("New first topic:", auto_factory_batch.peek_first_topic())

done_after = auto_factory_batch.get_done_topics()
print("Done topics count after:", len(done_after))
print("Done topics list:", done_after)
