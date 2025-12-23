"""
unit이 '알람존' ObjectType의 범위 안에 들어왔는지 확인하는 함수
"""


def insert_objects_in_alert():
    from graphio_sdk import GraphioClient
    from uuid import uuid4
    client = GraphioClient()

    try:
        Unit = client.ontology.get_object_type("유닛")
        Zone = client.ontology.get_object_type("지역")
        Alert = client.ontology.get_object_type("알람존")

        if not Unit:
            raise ValueError("'유닛' ObjectType을 찾을 수 없습니다.")

        # 조회 쿼리 구성
        unit_query = Unit.select('side', 'y', 'x')
        zone_query = Zone.select()

        # 데이터 조회
        units = unit_query.execute()
        zones = zone_query.execute()

        if not units:
            print("체크할 '유닛' 데이터가 없습니다.")
            return {
                "updated_count": 0,
                "results": None
            }

        print(f"조회된 '유닛' 데이터: {len(units)}건")
        edits = client.ontology.edits()
        updated_count = 0

        for unit in units:
            props = unit.get('properties')

            if props.get('side') == 'ALLY':
                continue

            x = props.get('x')
            y = props.get('y')

            # x, y 좌표가 없는 경우 건너뛰기
            if x is None or y is None:
                continue

            for z in zones:
                zone_props = z.get("properties", {})
                lx = zone_props.get("lx")
                ly = zone_props.get("ly")
                rx = zone_props.get("rx")
                ry = zone_props.get("ry")
                zone_name = zone_props.get("name")

                # 좌표 범위 확인
                if lx is not None and ly is not None and rx is not None and ry is not None:
                    if lx <= x <= rx and ly <= y <= ry:
                        edits.objects(Alert).create({
                            "objectTypeId": z.get('objectTypeId'),
                            "properties": {
                                "id": str(uuid4()),
                                "unit_element_id": unit.get('elementId'),
                                "zone_name": zone_name
                            }
                        })
                        updated_count += 1

        if updated_count == 0:
            print("수정할 데이터가 없습니다.")
            return {
                "updated_count": 0,
                "results": None
            }

        # 변경사항 커밋
        print(f"\n{updated_count}건의 변경사항을 커밋합니다...")
        results = edits.commit()

        print(f"✓ 업데이트 완료: {updated_count}건")

        return {
            "updated_count": updated_count,
            "results": results
        }
    except Exception as e:
        print(f"[check_objects_in_danger_zone] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        client.close()


if __name__ == "__main__":
    """
    사용 예제
    """
    insert_objects_in_alert()
