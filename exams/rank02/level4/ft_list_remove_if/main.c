#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ft_list.h"

void	ft_list_remove_if(t_list **begin_list, void *data_ref, int (*cmp)());

/* usage: ./a.out data_ref elem1 elem2 ... */
int	main(int argc, char **argv)
{
	t_list	*head;
	t_list	*node;
	int		i;

	if (argc < 2)
		return (0);
	head = NULL;
	i = argc - 1;
	while (i >= 2)
	{
		node = malloc(sizeof(t_list));
		node->data = strdup(argv[i]);
		node->next = head;
		head = node;
		i--;
	}
	ft_list_remove_if(&head, argv[1], strcmp);
	node = head;
	while (node)
	{
		printf("[%s] ", (char *)node->data);
		node = node->next;
	}
	printf("\n");
	return (0);
}
