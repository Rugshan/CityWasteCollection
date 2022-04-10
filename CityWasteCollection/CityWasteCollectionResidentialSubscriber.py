# Imports
import ast
import threading
import pika


# NotificationReceiver RabbitMQ Function
def NotificationReceiver(from_node, to_node, is_all):

    # Connection, Channel, Exchange
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='Notifier', exchange_type='fanout')

    # Randomly generate queue.
    result_queue = channel.queue_declare(queue='', exclusive=True)
    queue_name = result_queue.method.queue
    channel.queue_bind(exchange='Notifier', queue=queue_name)

    print('Waiting for notification messages...')

    # Callback function.
    def callback(ch, method, properties, body):

        # Decode body to dictionary.
        notification_info = body.decode("UTF-8")
        notification_info = ast.literal_eval(notification_info)
        notification_date_time = notification_info['date_time']
        notification_from_node = notification_info['from_node']
        notification_to_node = notification_info['to_node']

        # If is_all is False, display notifications for the specified edge.
        if not is_all:

            if notification_from_node == from_node and notification_to_node == to_node:

                # Print notification to user.
                print(f"{notification_date_time}: The waste between nodes [{notification_from_node}] and "
                      f"[{notification_to_node}] has successfully been collected.")

        elif is_all:

            # Print notification to user.
            print(f"{notification_date_time}: The waste between nodes [{notification_from_node}] and "
                  f"[{notification_to_node}] has successfully been collected.")

    # Start consuming.
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


# Main Function
def main():

    print('Do you want to enable notifications for all cleared blocks (edges) or a specific block (edge)?')
    print("For all notifications (edges), type 'all'. For a specific block (edge), enter the nodes of the edge. ")

    result = str(input("Enter your response: "))
    nodes = result.split(" ")

    if len(nodes) == 2:

        from_node = int(nodes[0])
        to_node = int(nodes[1])

        # Start Waste Logger Thread
        notifier_thread = threading.Thread(target=NotificationReceiver, args=[from_node, to_node, False])
        notifier_thread.start()

    else:

        # Start Waste Logger Thread
        notifier_thread = threading.Thread(target=NotificationReceiver, args=[0, 0, True])
        notifier_thread.start()


# Startup
if __name__ == '__main__':

    # Start main program.
    main()
