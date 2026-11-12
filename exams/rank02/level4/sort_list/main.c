#include <stdio.h>
#include <stdlib.h>
#include "list.h"

t_list	*sort_list(t_list *lst, int (*cmp)(int, int));

static int	ascending(int a, int b)
{
	return (a <= b);
}

static int	descending(int a, int b)
{
	return (a >= b);
}

static void	print_list(t_list *lst)
{
	while (lst)
	{
		printf("%d ", lst->data);
		lst = lst->next;
	}
	printf("\n");
}

int	main(int argc, char **argv)
{
	t_list	*head;
	t_list	*node;
	int		i;

	head = NULL;
	i = argc - 1;
	while (i >= 1)
	{
		node = malloc(sizeof(t_list));
		node->data = atoi(argv[i]);
		node->next = head;
		head = node;
		i--;
	}
	head = sort_list(head, ascending);
	print_list(head);
	head = sort_list(head, descending);
	print_list(head);
	return (0);
}
