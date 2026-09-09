import {
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import {
  mount,
} from '@vue/test-utils'

vi.mock(
  'vue-router',
  () => ({
    RouterLink: {
      name: 'RouterLink',
      props: [
        'to',
      ],
      template:
        '<a><slot /></a>',
    },

    useRouter: () => ({
      back: vi.fn(),
      push: vi.fn(),
    }),
  })
)

import NotFoundView from '../NotFoundView.vue'


describe(
  'NotFoundView',
  () => {
    it(
      'shows the 404 error message',
      () => {
        const wrapper =
          mount(NotFoundView)

        expect(
          wrapper.text()
        ).toContain(
          'Error 404'
        )

        expect(
          wrapper.text()
        ).toContain(
          'Parking space not found'
        )
      }
    )

    it(
      'provides navigation actions',
      () => {
        const wrapper =
          mount(NotFoundView)

        expect(
          wrapper.text()
        ).toContain(
          'Return home'
        )

        expect(
          wrapper.text()
        ).toContain(
          'Go back'
        )
      }
    )

    it(
      'links the home action to root',
      () => {
        const wrapper =
          mount(NotFoundView)

        const homeLink =
          wrapper.findComponent({
            name: 'RouterLink',
          })

        expect(
          homeLink.props('to')
        ).toBe('/')
      }
    )
  }
)
